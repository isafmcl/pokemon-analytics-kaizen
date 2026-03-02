"""Serviço para limpeza e normalização de dataframes de Pokemon."""
from __future__ import annotations

from logging import Logger

import pandas as pd

from core.exceptions import ValidationError


class PokemonCleaningService:
    """Serviço responsável por limpar atributos de Pokemon."""

    def __init__(self, *, logger: Logger) -> None:
        """Inicializa um novo ``PokemonCleaningService``."""

        self._logger = logger

    def clean_pokemon_dataframe(
        self,
        pokemon_df: pd.DataFrame,
        *,
        legendary_column: str = "legendary",
    ) -> pd.DataFrame:
        """Retorna uma cópia limpa do DataFrame de Pokemon."""

        if pokemon_df.empty:
            raise ValidationError("DataFrame de Pokemon está vazio")

        cleaned = pokemon_df.copy(deep=True)

        if "pokemon_id" not in cleaned.columns and "id" in cleaned.columns:
            self._logger.info(
                "Renomeando coluna 'id' para 'pokemon_id' para manter consistência",
            )
            cleaned = cleaned.rename(columns={"id": "pokemon_id"})

        if "generation" in cleaned.columns:
            cleaned["generation"] = pd.to_numeric(
                cleaned["generation"], errors="coerce"
            ).astype("Int64")

        if "types" in cleaned.columns and (
            "type_1" not in cleaned.columns or "type_2" not in cleaned.columns
        ):
            self._logger.info("Splitting 'types' column into 'type_1' and 'type_2'")
            type_1_values: list[str | None] = []
            type_2_values: list[str | None] = []
            for raw in cleaned["types"].astype("object"):
                type_1, type_2 = self._split_type_values(raw)
                type_1_values.append(type_1)
                type_2_values.append(type_2)

            if "type_1" not in cleaned.columns:
                cleaned["type_1"] = type_1_values
            if "type_2" not in cleaned.columns:
                cleaned["type_2"] = type_2_values

        if "type_1" in cleaned.columns:
            if "type_2" not in cleaned.columns:
                cleaned["type_2"] = None

            needs_split = cleaned["type_1"].astype("object").str.contains(r"[/,]")
            if needs_split.any():
                self._logger.info(
                    "Normalizing 'type_1' values that contain separators into 'type_1' and 'type_2'",
                )
                split_types = cleaned.loc[needs_split, "type_1"].astype("object")
                split_parts = split_types.apply(self._split_type_values)
                cleaned.loc[needs_split, "type_1"] = split_parts.map(lambda v: v[0])
                needs_type2 = needs_split & cleaned["type_2"].isna()
                cleaned.loc[needs_type2, "type_2"] = split_parts.map(lambda v: v[1])

        if legendary_column not in cleaned.columns:
            self._logger.info(
                "Legendary column '%s' not found; defaulting to False", legendary_column
            )
            cleaned[legendary_column] = False
        else:
            cleaned[legendary_column] = self._to_boolean_series(
                cleaned[legendary_column].astype("object"),
            )
        cleaned = self._normalize_stat_columns(cleaned)

        return cleaned

    @staticmethod
    def _split_type_values(raw: object) -> tuple[str | None, str | None]:
        """Divide valores de tipo em (type_1, type_2) usando separadores comuns."""

        if raw is None:
            return None, None
        text = str(raw).strip()
        if not text:
            return None, None

        normalized = text.replace("|", "/").replace(",", "/")
        parts = [p.strip() for p in normalized.split("/") if p.strip()]
        if not parts:
            return None, None
        if len(parts) == 1:
            return parts[0], None
        return parts[0], parts[1]

    @staticmethod
    def _to_boolean_series(series: pd.Series) -> pd.Series:
        """Converte uma série de valores mistos em booleanos."""

        truthy = {"true", "1", "yes", "y", "t"}

        def _convert(value: object) -> bool:
            if isinstance(value, bool):
                return value
            if value is None:
                return False
            text = str(value).strip().lower()
            return text in truthy

        return series.map(_convert).astype(bool)

    def _normalize_stat_columns(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nomes de colunas de atributos numéricos do Pokemon.

        O endpoint de detalhes de Pokemon pode variar a forma como
        escreve os atributos (por exemplo, "HP" em vez de "hp" ou
        "Sp. Atk" em vez de "sp_attack"). Aqui convertemos essas
        variações para nomes canônicos usados no restante da aplicação.
        """

        normalized = frame.copy(deep=True)

        mappings: dict[str, list[str]] = {
            "hp": ["hp", "HP", "Hp"],
            "attack": ["attack", "Attack", "atk", "Atk"],
            "defense": ["defense", "Defense", "def", "Def"],
            "sp_attack": [
                "sp_attack",
                "Sp_Attack",
                "sp_atk",
                "Sp. Atk",
                "special_attack",
                "Special Attack",
            ],
            "sp_defense": [
                "sp_defense",
                "Sp_Defense",
                "sp_def",
                "Sp. Def",
                "special_defense",
                "Special Defense",
            ],
            "speed": ["speed", "Speed"],
            "type_1": ["type_1", "Type_1", "Type 1", "type1", "Type1"],
            "type_2": ["type_2", "Type_2", "Type 2", "type2", "Type2"],
        }

        for target, candidates in mappings.items():
            if target in normalized.columns:
                continue
            for candidate in candidates:
                if candidate in normalized.columns and candidate != target:
                    self._logger.info(
                        "Renomeando coluna '%s' para '%s' para manter consistência",
                        candidate,
                        target,
                    )
                    normalized = normalized.rename(columns={candidate: target})
                    break

        return normalized
