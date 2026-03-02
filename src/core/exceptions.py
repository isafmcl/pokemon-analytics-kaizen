from __future__ import annotations
from typing import Any, Optional


class ApplicationError(Exception):

    def __init__(self, message: str, *, cause: Optional[BaseException] = None) -> None:

        super().__init__(message)
        self.cause = cause


class ConfigError(ApplicationError):
    """Erro de configuração da aplicação."""


class AuthError(ApplicationError):
    """Erro na autenticação com a API externa."""


class TokenExpiredError(AuthError):
    """Token de acesso expirado ou não pôde ser renovado."""


class ApiClientError(ApplicationError):
    """Classe base para erros relacionados ao cliente HTTP."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        payload: Optional[Any] = None,
        cause: Optional[BaseException] = None,
    ) -> None:

        super().__init__(message, cause=cause)
        self.status_code = status_code
        self.payload = payload


class ApiRequestError(ApiClientError):
    """Erro quando a API responde com um código de status não bem-sucedido."""


class PaginationError(ApiClientError):
    """Erro ao manipular respostas paginadas da API."""


class RepositoryError(ApplicationError):
    """Classe base para erros relacionados a repositórios."""


class DatabaseError(RepositoryError):
    """Erro em operação de banco de dados."""


class ValidationError(ApplicationError):
    """Erro de validação de dados na borda da aplicação."""