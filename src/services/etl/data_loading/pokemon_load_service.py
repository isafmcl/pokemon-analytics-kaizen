from __future__ import annotations
from logging import Logger
from typing import List, Sequence
import pandas as pd
from core.exceptions import DatabaseError, ValidationError
from database.models import Pokemon
from repositories.pokemon_repository import PokemonRepository

class PokemonLoadService:
    def __init__(
        self,
        *,
        repository: PokemonRepository,
        logger: Logger,
    ) -> None:


        self._repository = repository
        self._logger = logger

    def load_pokemon(
        self,
        pokemon_df: pd.DataFrame,
        *,
        id_column: str = "pokemon_id",
        name_column: str = "name",
        type_1_column: str = "type_1",
        type_2_column: str = "type_2",
        generation_column: str = "generation",
        legendary_column: str = "legendary",
        hp_column: str = "hp",
        attack_column: str = "attack",
        defense_column: str = "defense",
        sp_attack_column: str = "sp_attack",
        sp_defense_column: str = "sp_defense",
        speed_column: str = "speed",
    ) -> int:
        """Persiste dados mestres de Pokemon de forma idempotente."""

        if pokemon_df.empty:
            self._logger.info("Pokemon DataFrame is empty; nothing to load")
            return 0

        required_columns = [
            id_column,
            name_column,
            legendary_column,
        ]

        self._ensure_columns_present(
            pokemon_df,
            required_columns,
            frame_name="pokemon_df",
        )

        pokemon_ids = [int(x) for x in pokemon_df[id_column].tolist()]
        existing_ids = set(self._repository.get_existing_pokemon_ids(pokemon_ids))

        new_rows = pokemon_df[~pokemon_df[id_column].isin(existing_ids)]
        existing_rows = pokemon_df[pokemon_df[id_column].isin(existing_ids)]

        inserted = 0

        if not new_rows.empty:
            new_entities: List[Pokemon] = []
            for _, row in new_rows.iterrows():
                entity = Pokemon(
                    pokemon_id=int(row[id_column]),
                    name=str(row[name_column]),
                    type_1=self._safe_str(row.get(type_1_column)),
                    type_2=self._safe_str(row.get(type_2_column)),
                    generation=self._safe_int(row.get(generation_column)),
                    legendary=bool(row[legendary_column]),
                    hp=self._safe_int(row.get(hp_column)),
                    attack=self._safe_int(row.get(attack_column)),
                    defense=self._safe_int(row.get(defense_column)),
                    sp_attack=self._safe_int(row.get(sp_attack_column)),
                    sp_defense=self._safe_int(row.get(sp_defense_column)),
                    speed=self._safe_int(row.get(speed_column)),
                )
                new_entities.append(entity)

            self._logger.info(
                "Inserindo %s novos registros de Pokemon",
                len(new_entities),
            )
            try:
                self._repository.add_many(new_entities)
                self._repository.commit()
            except DatabaseError:
                self._repository.rollback()
                raise
            inserted = len(new_entities)

        if not existing_rows.empty:
            self._logger.info(
                "Atualizando %s registros de Pokemon já existentes com os atributos mais recentes",
                len(existing_rows),
            )
            try:
                id_to_row = {
                    int(row[id_column]): row for _, row in existing_rows.iterrows()
                }

                q = self._repository._session.query(Pokemon).filter(
                    Pokemon.pokemon_id.in_(list(id_to_row.keys()))
                )
                for entity in q.all():
                    row = id_to_row.get(entity.pokemon_id)
                    if row is None:
                        continue
                    entity.name = str(row[name_column])
                    entity.type_1 = self._safe_str(row.get(type_1_column))
                    entity.type_2 = self._safe_str(row.get(type_2_column))
                    entity.generation = self._safe_int(row.get(generation_column))
                    entity.legendary = bool(row[legendary_column])
                    entity.hp = self._safe_int(row.get(hp_column))
                    entity.attack = self._safe_int(row.get(attack_column))
                    entity.defense = self._safe_int(row.get(defense_column))
                    entity.sp_attack = self._safe_int(row.get(sp_attack_column))
                    entity.sp_defense = self._safe_int(row.get(sp_defense_column))
                    entity.speed = self._safe_int(row.get(speed_column))

                self._repository.commit()
            except DatabaseError:
                self._repository.rollback()
                raise

        if inserted == 0 and existing_rows.empty:
            self._logger.info(
                "Todos os Pokemon já existiam; atributos atualizados quando aplicável"
            )

        return inserted

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

    @staticmethod
    def _safe_int(value: object | None) -> int | None:
        """Converte um valor para ``int`` ou retorna ``None`` em caso de falha."""

        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_str(value: object | None) -> str | None:
        """Converte um valor para ``str`` ou retorna ``None`` em caso de falha."""

        if value is None:
            return None
        text = str(value).strip()
        return text or None
