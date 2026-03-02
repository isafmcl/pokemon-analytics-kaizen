from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Pokemon(Base):
    __tablename__ = "pokemon"

    pokemon_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    type_1: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    type_2: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    generation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    legendary: Mapped[bool] = mapped_column(Boolean, index=True, default=False)

    hp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    attack: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    defense: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sp_attack: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sp_defense: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    speed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_pokemon_type_1_type_2", "type_1", "type_2"),
    )


class Combat(Base):
    __tablename__ = "combat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    first_pokemon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pokemon.pokemon_id"),
        index=True,
    )
    second_pokemon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pokemon.pokemon_id"),
        index=True,
    )
    winner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pokemon.pokemon_id"),
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "first_pokemon_id",
            "second_pokemon_id",
            "winner_id",
            name="uq_combat_unique_battle",
        ),
        Index("ix_combat_first_second", "first_pokemon_id", "second_pokemon_id"),
    )
