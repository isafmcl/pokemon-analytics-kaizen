from __future__ import annotations
from dataclasses import dataclass
from logging import Logger
from typing import Optional
import requests
from sqlalchemy.orm import Session
from config.logger import get_logger
from config.settings import get_settings
from database.session import create_session
from repositories.combat_repository import CombatRepository
from repositories.pokemon_repository import PokemonRepository
from services.http.api_client import ApiClient
from services.http.auth_service import AuthService
from services.etl.data_extraction.extract_service import ExtractService
from services.etl.data_loading.load_service import LoadService
from services.etl.data_transformation.transform_service import TransformService


@dataclass(frozen=True)
class EtlContext:
    logger: Logger
    extract_service: ExtractService
    transform_service: TransformService
    load_service: LoadService
    db_session: Session


def _build_http_session() -> requests.Session:
    return requests.Session()


def build_etl_context() -> EtlContext:
    settings = get_settings()

    root_logger = get_logger("etl")

    http_session = _build_http_session()

    auth_service = AuthService(
        session=http_session,
        base_url=settings.api_base_url,
        username=settings.api_username,
        password=settings.api_password,
        timeout_seconds=settings.request_timeout_seconds,
        logger=get_logger("services.auth"),
    )

    api_client = ApiClient(
        session=http_session,
        base_url=settings.api_base_url,
        auth_service=auth_service,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.max_retries,
        logger=get_logger("services.api_client"),
    )

    extract_service = ExtractService(
        api_client=api_client,
        default_page_size=settings.page_size_default,
        logger=get_logger("services.extract"),
    )

    transform_service = TransformService(
        logger=get_logger("services.transform"),
    )

    db_session = create_session()

    pokemon_repo = PokemonRepository(
        session=db_session,
        logger=get_logger("repo.pokemon"),
    )
    combat_repo = CombatRepository(
        session=db_session,
        logger=get_logger("repo.combat"),
    )

    load_service = LoadService(
        session=db_session,
        pokemon_repository=pokemon_repo,
        combat_repository=combat_repo,
        logger=get_logger("services.load"),
    )

    return EtlContext(
        logger=root_logger,
        extract_service=extract_service,
        transform_service=transform_service,
        load_service=load_service,
        db_session=db_session,
    )


def run_etl_pipeline(context: Optional[EtlContext] = None) -> None:
    etl_context = context or build_etl_context()
    logger = etl_context.logger

    try:
        logger.info("Iniciando extração de Pokemon (lista)")
        pokemon_raw_df = etl_context.extract_service.fetch_all_pokemon()

        if "pokemon_id" in pokemon_raw_df.columns:
            base_ids = pokemon_raw_df["pokemon_id"].tolist()
        elif "id" in pokemon_raw_df.columns:
            base_ids = pokemon_raw_df["id"].tolist()
        else:
            base_ids = []

        logger.info("Iniciando extração de detalhes de Pokemon por ID")
        pokemon_details_df = etl_context.extract_service.fetch_pokemon_details_for_ids(
            base_ids
        )

        if not pokemon_details_df.empty:
            pokemon_source_df = pokemon_details_df
        else:
            logger.warning(
                "Falha ao obter detalhes de Pokemon; usando apenas dados da lista"
            )
            pokemon_source_df = pokemon_raw_df

        logger.info("Iniciando extração de Combats")
        combats_raw_df = etl_context.extract_service.fetch_all_combats()
        logger.info(
            "Combates brutos extraídos da API: %s registros",
            combats_raw_df.shape[0],
        )

        logger.info("Transformando dados de Pokemon")
        pokemon_clean_df = etl_context.transform_service.clean_pokemon_dataframe(
            pokemon_source_df
        )

        logger.info("Calculando métricas de batalha")
        pokemon_metrics_df = etl_context.transform_service.build_pokemon_battle_metrics(
            pokemon_df=pokemon_clean_df,
            combats_df=combats_raw_df,
        )

        logger.info("Carregando Pokemon para o banco (idempotente)")
        novos_pokemon = etl_context.load_service.load_pokemon(pokemon_metrics_df)
        logger.info("Novos Pokemon inseridos: %s", novos_pokemon)

        logger.info("Carregando Combats para o banco (idempotente)")
        novos_combats = etl_context.load_service.load_combats(combats_raw_df)
        logger.info("Novos Combats inseridos: %s", novos_combats)

    finally:
        etl_context.db_session.close()
