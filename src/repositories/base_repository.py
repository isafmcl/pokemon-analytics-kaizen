from __future__ import annotations
from typing import Generic, Iterable, List, Optional, Sequence, Type, TypeVar
from logging import Logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from core.exceptions import DatabaseError


TModel = TypeVar("TModel")


class BaseRepository(Generic[TModel]):
    def __init__(
        self,
        *,
        model_class: Type[TModel],
        session: Session,
        logger: Logger,
    ) -> None:
        self._model_class = model_class
        self._session = session
        self._logger = logger

    @property
    def model_class(self) -> Type[TModel]:
        return self._model_class

    def add(self, entity: TModel) -> None:
        self._session.add(entity)

    def add_many(self, entities: Iterable[TModel]) -> None:
        self._session.add_all(list(entities))

    def get_by_id(self, entity_id: int) -> Optional[TModel]:
        return self._session.get(self._model_class, entity_id)

    def list_all(self) -> List[TModel]:
        return list(self._session.query(self._model_class).all())

    def delete(self, entity: TModel) -> None:
        self._session.delete(entity)

    def flush(self) -> None:
        try:
            self._session.flush()
        except SQLAlchemyError as exc:
            self._logger.error("Erro ao fazer flush da sessão", exc_info=True)
            raise DatabaseError("Erro ao fazer flush da sessão") from exc

    def commit(self) -> None:
        try:
            self._session.commit()
        except SQLAlchemyError as exc:
            self._logger.error("Erro ao efetivar commit da sessão", exc_info=True)
            raise DatabaseError("Erro ao efetivar commit da sessão") from exc

    def rollback(self) -> None:
        try:
            self._session.rollback()
        except SQLAlchemyError:
            self._logger.error("Erro ao executar rollback da sessão", exc_info=True)

    def get_existing_ids(self, ids: Sequence[int]) -> List[int]:
        """Retorna IDs que já existem no banco de dados."""

        if not ids:
            return []

        pk_column = getattr(self._model_class, "pokemon_id", None) or getattr(
            self._model_class, "id", None
        )
        if pk_column is None:
            raise DatabaseError("O modelo não expõe uma chave primária identificável")

        query = self._session.query(pk_column).filter(pk_column.in_(ids))
        return [row[0] for row in query.all()]
