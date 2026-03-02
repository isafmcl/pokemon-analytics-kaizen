"""Serviço de extração de dados com paginação automática.

Este serviço apenas orquestra chamadas ao ``ApiClient`` e retorna
os dados como ``pandas.DataFrame``, escondendo os detalhes de paginação
(``page``/``per_page``) das camadas superiores.

Nenhuma transformação ou regra de negócio deve existir aqui; apenas
extração e paginação.

"""
from __future__ import annotations

from logging import Logger
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import pandas as pd

from core.exceptions import PaginationError
from services.http.api_client import ApiClient


class ExtractService:
    """Extrator de dados de alto nível para recursos da API de Pokemon."""

    def __init__(
        self,
        *,
        api_client: ApiClient,
        default_page_size: int,
        logger: Logger,
    ) -> None:
        """Inicializa uma nova instância de ``ExtractService``."""

        self._api_client = api_client
        self._default_page_size = default_page_size
        self._logger = logger

    def fetch_all_pokemon(
        self,
        *,
        page_size: Optional[int] = None,
        max_records: Optional[int] = None,
    ) -> pd.DataFrame:
        """Busca todos os registros de Pokemon com paginação automática."""

        effective_page_size = page_size or self._default_page_size
        max_page_size = 50
        if effective_page_size > max_page_size:
            effective_page_size = max_page_size
        self._logger.info(
            "Iniciando extração de Pokemon com page_size=%s, max_records=%s",
            effective_page_size,
            max_records,
        )

        records: List[Dict[str, Any]] = []
        page = 1
        fetched = 0

        while True:
            if max_records is not None and fetched >= max_records:
                break

            current_page_size = self._compute_current_limit(
                effective_page_size=effective_page_size,
                offset=fetched,
                max_records=max_records,
            )

            if current_page_size <= 0:
                break

            page_payload = self._api_client.get_pokemon(
                page=page,
                per_page=current_page_size,
            )

            page_records = self._extract_records_from_payload(page_payload)

            if not page_records:
                break

            records.extend(page_records)
            fetched += len(page_records)

            if len(page_records) < current_page_size:
                break

            page += 1

        return pd.DataFrame.from_records(records)

    def fetch_pokemon_details_for_ids(
        self,
        pokemon_ids: Sequence[int],
    ) -> pd.DataFrame:
        """Busca detalhes de Pokemon para uma lista de IDs."""

        if not pokemon_ids:
            return pd.DataFrame()

        records: List[Dict[str, Any]] = []
        unique_ids = list(dict.fromkeys(int(pid) for pid in pokemon_ids))

        for pid in unique_ids:
            try:
                payload = self._api_client.get_pokemon_by_id(pid)
            except Exception as exc:
                self._logger.warning(
                    "Falha ao buscar detalhes para o Pokemon id=%s: %s",
                    pid,
                    exc,
                )
                continue

            if isinstance(payload, Mapping):
                records.append(dict(payload))
            else:
                self._logger.warning(
                    "Unexpected payload type for Pokemon id=%s: %s", pid, type(payload)
                )

        return pd.DataFrame.from_records(records)

    def fetch_all_combats(
        self,
        *,
        page_size: Optional[int] = None,
        max_records: Optional[int] = None,
    ) -> pd.DataFrame:
        """Busca todos os registros de combates com paginação automática."""

        effective_page_size = page_size or self._default_page_size
        max_page_size = 50
        if effective_page_size > max_page_size:
            effective_page_size = max_page_size
        self._logger.info(
            "Iniciando extração de combates com page_size=%s, max_records=%s",
            effective_page_size,
            max_records,
        )

        records: List[Dict[str, Any]] = []
        page = 1
        fetched = 0

        while True:
            if max_records is not None and fetched >= max_records:
                break

            current_page_size = self._compute_current_limit(
                effective_page_size=effective_page_size,
                offset=fetched,
                max_records=max_records,
            )

            if current_page_size <= 0:
                break

            page_payload = self._api_client.get_combats(
                page=page,
                per_page=current_page_size,
            )

            page_records = self._extract_records_from_payload(page_payload)

            if not page_records:
                break

            records.extend(page_records)
            fetched += len(page_records)

            if len(page_records) < current_page_size:
                break

            page += 1

        return pd.DataFrame.from_records(records)

    @staticmethod
    def _compute_current_limit(
        *,
        effective_page_size: int,
        offset: int,
        max_records: Optional[int],
    ) -> int:
        """Calcula o limite da página atual respeitando ``max_records``."""

        if max_records is None:
            return effective_page_size

        remaining = max_records - offset
        if remaining <= 0:
            return 0
        return min(effective_page_size, remaining)

    def _extract_records_from_payload(self, payload: Any) -> List[Dict[str, Any]]:
        """Normaliza o payload da API em uma lista de dicionários.

        Registros individuais que não puderem ser normalizados são
        ignorados com log de aviso, em vez de derrubar todo o ETL.
        """

        def _normalize_list(items: Iterable[Any]) -> List[Dict[str, Any]]:
            registros: List[Dict[str, Any]] = []
            for item in items:
                try:
                    registros.append(self._ensure_mapping(item))
                except PaginationError as exc:
                    self._logger.warning(
                        "Ignorando registro inválido no payload paginado: %s",
                        exc,
                    )
            return registros

        if isinstance(payload, list):
            return _normalize_list(payload)

        if isinstance(payload, Mapping):
            for key in ("results", "items", "data", "pokemons", "combats"):
                candidate = payload.get(key)
                if isinstance(candidate, list):
                    return _normalize_list(candidate)

        self._logger.error(
            "Estrutura de payload paginado não suportada: %s",
            type(payload),
        )
        raise PaginationError("Estrutura de payload paginado não suportada")

    @staticmethod
    def _ensure_mapping(record: Any) -> Dict[str, Any]:
        """Garante que um registro seja retornado como dicionário."""

        if isinstance(record, Mapping):
            return dict(record)

        if hasattr(record, "dict") and callable(getattr(record, "dict")):
            result = record.dict()
            if isinstance(result, Mapping):
                return dict(result)

        raise PaginationError("Registro não é um mapeamento e não pode ser normalizado")
