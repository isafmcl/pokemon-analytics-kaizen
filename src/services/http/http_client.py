"""Cliente HTTP base para requisições à API.

Este módulo contém a lógica fundamental de requisições HTTP sem inteligência
de autenticação ou tratamento especial de status codes.

"""
from __future__ import annotations

from logging import Logger
from typing import Any, Mapping, Optional

import requests
from requests import Response, Session

from core.exceptions import ApiClientError


class HttpClient:
    """Cliente HTTP simples para requisições básicas à API."""

    def __init__(
        self,
        *,
        session: Session,
        base_url: str,
        timeout_seconds: float,
        logger: Logger,
    ) -> None:
        """Inicializa um novo HttpClient."""
        self._session = session
        self._base_url = str(base_url).rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._logger = logger

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> Response:
        """Executa uma requisição HTTP básica sem retry ou tratamento especial.
        
        Args:
            method: GET, POST, etc.
            path: /pokemon, /combats, etc.
            params: Parâmetros de query string.
            json_body: Corpo JSON da requisição.
            headers: Cabeçalhos HTTP customizados.
            
        Returns:
            Response da requisição.
            
        Raises:
            ApiClientError: Se houver erro de conexão ou timeout.
        """
        url = f"{self._base_url}{path}"
        request_headers = headers or {}

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=dict(params) if params is not None else None,
                json=dict(json_body) if json_body is not None else None,
                headers=request_headers,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            self._logger.error(
                "Requisição HTTP para %s falhou",
                url,
                exc_info=True,
            )
            raise ApiClientError("Falha na requisição HTTP", cause=exc)

        return response

    def _parse_json(self, response: Response) -> Any:
        """Faz o parse do corpo JSON da resposta.
        
        Args:
            response: Response da requisição.
            
        Returns:
            Dados parseados como JSON (dict, list, etc).
            
        Raises:
            ApiClientError: Se o JSON for inválido.
        """
        try:
            return response.json()
        except ValueError as exc:
            self._logger.error("Falha ao decodificar resposta JSON", exc_info=True)
            raise ApiClientError("Falha ao decodificar resposta JSON", cause=exc)

    @staticmethod
    def _safe_response_text(response: Response) -> str:
        """Extrai o texto da resposta de forma segura para logs.
        
        Limita o tamanho para evitar logs muito longos.
        
        Args:
            response: Response da requisição.
            
        Returns:
            Texto da resposta (truncado se necessário).
        """
        text = response.text or ""
        max_length = 500
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
