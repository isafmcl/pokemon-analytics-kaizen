from __future__ import annotations
from logging import Logger
from typing import List, Sequence, Tuple
import pandas as pd

from core.exceptions import DatabaseError, ValidationError
from database.models import Combat
from repositories.combat_repository import CombatRepository
from repositories.pokemon_repository import PokemonRepository


class CombatLoadService:
    """Serviço que realiza carga em lote idempotente de registros de combate."""

    def __init__(
        self,
        *,
        repository: CombatRepository,
        pokemon_repository: PokemonRepository,
        logger: Logger,
    ) -> None:
        """Inicializa um novo ``CombatLoadService``."""

        self._repository = repository
        self._pokemon_repository = pokemon_repository
        self._logger = logger

    def load_combats(
        self,
        combats_df: pd.DataFrame,
        *,
        first_pokemon_column: str = "first_pokemon_id",
        second_pokemon_column: str = "second_pokemon_id",
        winner_column: str = "winner_id",
    ) -> int:
        """Persiste registros de combate de forma idempotente."""

        total_bruto = int(combats_df.shape[0])

        if combats_df.empty:
            self._logger.info("DataFrame de combates está vazio; nada a carregar")
            return 0

        self._logger.info(
            "Iniciando carga de combates: %s registros brutos recebidos do ETL",
            total_bruto,
        )

        combats_normalized = self._normalize_combat_columns(
            combats_df,
            first_pokemon_column=first_pokemon_column,
            second_pokemon_column=second_pokemon_column,
            winner_column=winner_column,
        )

        all_ids_series = pd.concat(
            [
                combats_normalized[first_pokemon_column],
                combats_normalized[second_pokemon_column],
                combats_normalized[winner_column],
            ],
            ignore_index=True,
        )

        all_ids = (
            pd.to_numeric(all_ids_series, errors="coerce")
            .dropna()
            .astype(int)
            .tolist()
        )

        valid_ids = set(self._pokemon_repository.get_existing_pokemon_ids(all_ids))

        combats_normalized[first_pokemon_column] = pd.to_numeric(
            combats_normalized[first_pokemon_column], errors="coerce"
        ).astype("Int64")
        combats_normalized[second_pokemon_column] = pd.to_numeric(
            combats_normalized[second_pokemon_column], errors="coerce"
        ).astype("Int64")
        combats_normalized[winner_column] = pd.to_numeric(
            combats_normalized[winner_column], errors="coerce"
        ).astype("Int64")

        mask = (
            combats_normalized[first_pokemon_column].isin(valid_ids)
            & combats_normalized[second_pokemon_column].isin(valid_ids)
            & combats_normalized[winner_column].isin(valid_ids)
        )

        filtered_combats = combats_normalized[mask]
        dropped = len(combats_normalized) - len(filtered_combats)
        if dropped > 0:
            self._logger.warning(
                "Ignorando %s combates que referenciam IDs de Pokemon desconhecidos",
                dropped,
            )

        # Additional safety: filter out combats with Pokemon ID > 799
        mask_valid_ids = (
            (filtered_combats[first_pokemon_column] <= 799)
            & (filtered_combats[second_pokemon_column] <= 799)
            & (filtered_combats[winner_column] <= 799)
        )
        filtered_combats = filtered_combats[mask_valid_ids]
        extra_dropped = len(combats_normalized[mask]) - len(filtered_combats)
        if extra_dropped > 0:
            self._logger.warning(
                "Ignorando %s combates com Pokemon ID > 799 como camada adicional de segurança",
                extra_dropped,
            )

        required_columns = [
            first_pokemon_column,
            second_pokemon_column,
            winner_column,
        ]
        self._ensure_columns_present(
            filtered_combats,
            required_columns,
            frame_name="combats_df",
        )

        all_keys: List[Tuple[int, int, int]] = []
        for _, row in filtered_combats.iterrows():
            key = (
                int(row[first_pokemon_column]),
                int(row[second_pokemon_column]),
                int(row[winner_column]),
            )
            all_keys.append(key)

        unique_keys_dict = dict.fromkeys(all_keys)
        unique_keys: List[Tuple[int, int, int]] = list(unique_keys_dict.keys())

        duplicates_in_source = len(all_keys) - len(unique_keys)
        if duplicates_in_source > 0:
            self._logger.warning(
                "Ignorando %s combates duplicados presentes no payload de origem",
                duplicates_in_source,
            )

        existing_keys = set(
            self._repository.get_existing_combat_keys(unique_keys)
        )

        new_entities: List[Combat] = []
        for key in unique_keys:
            if key in existing_keys:
                continue
            first_id, second_id, winner_id = key
            entity = Combat(
                first_pokemon_id=first_id,
                second_pokemon_id=second_id,
                winner_id=winner_id,
            )
            new_entities.append(entity)

        total_unicos_pos_filtros = len(unique_keys)
        total_existentes = total_unicos_pos_filtros - len(new_entities)

        self._logger.info(
            "Resumo da carga de combates: brutos=%s, invalidos_por_pokemon=%s, duplicados_na_origem=%s, unicos_pos_filtros=%s, ja_existiam_no_banco=%s, novos_a_inserir=%s",
            total_bruto,
            dropped,
            duplicates_in_source,
            total_unicos_pos_filtros,
            total_existentes,
            len(new_entities),
        )

        if not new_entities:
            self._logger.info("Todos os combates já existiam; nada novo a inserir")
            return 0

        self._logger.info(
            "Inserindo %s novos registros de combate",
            len(new_entities),
        )

        try:
            self._repository.add_many(new_entities)
            self._repository.commit()
        except DatabaseError:
            self._repository.rollback()
            raise

        return len(new_entities)

    def _normalize_combat_columns(
        self,
        combats_df: pd.DataFrame,
        *,
        first_pokemon_column: str,
        second_pokemon_column: str,
        winner_column: str,
    ) -> pd.DataFrame:
        """Normaliza colunas identificadoras de combate de nomes da API para *_id internos."""

        normalized = combats_df.copy(deep=True)
        rename_map: dict[str, str] = {}

        if first_pokemon_column not in normalized.columns and "first_pokemon" in normalized.columns:
            self._logger.info(
                "Renaming combats column 'first_pokemon' to '%s' for consistency",
                first_pokemon_column,
            )
            rename_map["first_pokemon"] = first_pokemon_column

        if second_pokemon_column not in normalized.columns and "second_pokemon" in normalized.columns:
            self._logger.info(
                "Renaming combats column 'second_pokemon' to '%s' for consistency",
                second_pokemon_column,
            )
            rename_map["second_pokemon"] = second_pokemon_column

        if winner_column not in normalized.columns and "winner" in normalized.columns:
            self._logger.info(
                "Renaming combats column 'winner' to '%s' for consistency",
                winner_column,
            )
            rename_map["winner"] = winner_column

        if rename_map:
            normalized = normalized.rename(columns=rename_map)

        return normalized

    def _ensure_columns_present(
        self,
        frame: pd.DataFrame,
        required_columns: Sequence[str],
        *,
        frame_name: str,
    ) -> None:
        """Valida se um DataFrame contém as colunas esperadas."""

        missing = [col for col in required_columns if col not in frame.columns]
        if missing:
            raise ValidationError(
                f"DataFrame '{frame_name}' não contém as colunas obrigatórias: {missing}"
            )

