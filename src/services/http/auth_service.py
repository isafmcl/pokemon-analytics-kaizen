from __future__ import annotations
from logging import Logger
from typing import Dict, Optional
import requests
from requests import Response, Session
from core.exceptions import AuthError


class AuthService:
    def __init__(
        self,
        *,
        session: Session,
        base_url: str,
        username: str,
        password: str,
        timeout_seconds: float,
        logger: Logger,
    ) -> None:

        self._session = session
        self._base_url = str(base_url).rstrip("/")
        self._username = username
        self._password = password
        self._timeout_seconds = timeout_seconds
        self._logger = logger

        self._access_token: Optional[str] = None

    @property
    def access_token(self) -> Optional[str]:
        """Retorna o token de acesso em cache, se existir."""

        return self._access_token

    def get_access_token(self, *, force_refresh: bool = False) -> str:
        """Retorna um token de acesso válido, renovando se necessário."""

        if self._access_token is None or force_refresh:
            self._logger.info("Solicitando novo token de acesso para a API")
            self._access_token = self._login()

        return self._access_token

    def build_auth_headers(self) -> Dict[str, str]:
        """Monta o cabeçalho Authorization usando o token atual."""

        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def _login(self) -> str:
        """Executa a requisição de login na API e retorna o token."""

        url = f"{self._base_url}/login"
        payload = {"username": self._username, "password": self._password}

        try:
            response: Response = self._session.post(
                url,
                json=payload,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            self._logger.error(
                "Erro ao chamar endpoint de autenticação",
                exc_info=True,
            )
            raise AuthError("Falha ao chamar endpoint de autenticação") from exc

        if response.status_code != 200:
            self._logger.warning(
                "Autenticação falhou com status %s", response.status_code
            )
            raise AuthError(
                f"Autenticação falhou com código de status {response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            self._logger.error("JSON inválido na resposta de autenticação", exc_info=True)
            raise AuthError("JSON inválido na resposta de autenticação") from exc

        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            self._logger.error("Resposta de autenticação sem campo access_token")
            raise AuthError("Resposta de autenticação não contém um access token válido")
        self._logger.info("Novo token de acesso obtido com sucesso")
        return token
