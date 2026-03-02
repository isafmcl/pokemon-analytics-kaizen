from __future__ import annotations
from logging import Logger
import time
from typing import Any, Dict, Mapping, Optional
import requests
from requests import Response, Session
from core.exceptions import (
    ApiRequestError,
    ApiClientError,
    TokenExpiredError,
    AuthError,
)
from .auth_service import AuthService
from .http_client import HttpClient


class ApiClient(HttpClient):
    """Cliente HTTP inteligente para a API de Pokemon com retry e autenticação."""

    def __init__(
        self,
        *,
        session: Session,
        base_url: str,
        auth_service: AuthService,
        timeout_seconds: float,
        max_retries: int,
        logger: Logger,
    ) -> None:
        super().__init__(
            session=session,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            logger=logger,
        )
        self._auth_service = auth_service
        self._max_retries = max_retries

    def get_pokemon(self, *, page: int, per_page: int) -> Any:
        """Busca uma página de Pokemons na API."""

        params: Dict[str, Any] = {"page": page, "per_page": per_page}
        response = self._request("GET", "/pokemon", params=params)
        return self._parse_json(response)

    def get_pokemon_by_id(self, pokemon_id: int) -> Any:
        """Busca os detalhes de um único Pokemon."""

        path = f"/pokemon/{pokemon_id}"
        response = self._request("GET", path)
        return self._parse_json(response)

    def get_combats(self, *, page: int, per_page: int) -> Any:
        """Busca uma página de combates na API."""

        params: Dict[str, Any] = {"page": page, "per_page": per_page}
        response = self._request("GET", "/combats", params=params)
        return self._parse_json(response)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Response:
        """Executa uma requisição HTTP com tentativa automática após 401."""

        url = f"{self._base_url}{path}"

        headers = self._auth_service.build_auth_headers()

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=dict(params) if params is not None else None,
                json=dict(json_body) if json_body is not None else None,
                headers=headers,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            self._logger.error(
                "Requisição HTTP para %s falhou na primeira tentativa",
                url,
                exc_info=True,
            )
            raise ApiClientError("Falha na requisição HTTP", cause=exc)

        if response.status_code == 429:
            for attempt in range(1, self._max_retries + 1):
                delay_seconds = min(60.0, float(2**attempt))
                self._logger.warning(
                    "Recebido 429 Too Many Requests de %s; aguardando %.1fs antes da tentativa %s/%s",
                    url,
                    delay_seconds,
                    attempt,
                    self._max_retries,
                )
                time.sleep(delay_seconds)

                try:
                    response = self._session.request(
                        method=method,
                        url=url,
                        params=dict(params) if params is not None else None,
                        json=dict(json_body) if json_body is not None else None,
                        headers=headers,
                        timeout=self._timeout_seconds,
                    )
                except requests.RequestException as exc:
                    self._logger.error(
                        "Requisição HTTP para %s falhou durante retry por limite de taxa",
                        url,
                        exc_info=True,
                    )
                    raise ApiClientError(
                        "Falha na requisição HTTP durante retry por limite de taxa",
                        cause=exc,
                    )

                if response.status_code != 429:
                    break

            if response.status_code == 429:
                self._logger.error(
                    "Limite de requisições da API excedido para %s após %s tentativas",
                    url,
                    self._max_retries,
                )
                raise ApiRequestError(
                    "Limite de requisições da API excedido",
                    status_code=response.status_code,
                    payload=self._safe_response_text(response),
                )

        if response.status_code == 401:
            self._logger.info(
                "Recebido 401; tentando atualizar o token e repetir a requisição"
            )

            refreshed_headers = self._refresh_token_and_build_headers()

            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=dict(params) if params is not None else None,
                    json=dict(json_body) if json_body is not None else None,
                    headers=refreshed_headers,
                    timeout=self._timeout_seconds,
                )
            except requests.RequestException as exc:
                self._logger.error(
                    "Requisição HTTP para %s falhou após renovação de token",
                    url,
                    exc_info=True,
                )
                raise ApiClientError(
                    "Falha na requisição HTTP após renovação de token",
                    cause=exc,
                )

            if response.status_code == 401:
                self._logger.error("Token permanece inválido após tentativa de renovação")
                raise TokenExpiredError("Token permanece inválido após renovação")

        if not 200 <= response.status_code < 300:
            self._logger.error(
                "Requisição para %s retornou status %s",
                url,
                response.status_code,
            )
            raise ApiRequestError(
                f"Requisição para a API falhou com código de status {response.status_code}",
                status_code=response.status_code,
                payload=self._safe_response_text(response),
            )

        return response

    def _refresh_token_and_build_headers(self) -> Dict[str, str]:
        """Renova o token de acesso e retorna os cabeçalhos atualizados."""

        try:
            token = self._auth_service.get_access_token(force_refresh=True)
        except AuthError as exc:
            self._logger.error("Falha ao renovar token", exc_info=True)
            raise TokenExpiredError("Falha ao renovar token") from exc

        return {"Authorization": f"Bearer {token}"}
