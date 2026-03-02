from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class ValidacaoResult:
    checagem: str
    resultado: int | str
    status: str


class ETLValidator:
    @staticmethod
    def validar_pokemon_ids(pokemon_df: pd.DataFrame) -> tuple[ValidacaoResult, ValidacaoResult]:
        """
        Valida IDs de Pokémon (nulos e duplicados).  
        Retorno:
            Tuple com resultados de validação de nulos e duplicados.
        """
        missing_ids = (
            pokemon_df["pokemon_id"].isna().sum()
            if "pokemon_id" in pokemon_df.columns
            else 0
        )
        dup_ids = (
            pokemon_df["pokemon_id"].duplicated().sum()
            if "pokemon_id" in pokemon_df.columns
            else 0
        )
        
        result_null = ValidacaoResult(
            checagem="pokemon_id nulo",
            resultado=int(missing_ids),
            status="OK" if missing_ids == 0 else "FALHA",
        )
        
        result_dup = ValidacaoResult(
            checagem="pokemon_id duplicado",
            resultado=int(dup_ids),
            status="OK" if dup_ids == 0 else "FALHA",
        )
        
        return result_null, result_dup
    
    @staticmethod
    def validar_combate_vencedores(combats_df: pd.DataFrame) -> tuple[ValidacaoResult, ValidacaoResult]:
        if "winner_id" not in combats_df.columns:
            return (
                ValidacaoResult("winner nulo", 0, "OK"),
                ValidacaoResult("winner fora do par", 0, "OK"),
            )
        
        winners = combats_df["winner_id"]
        null_winner = winners.isna().sum()
        
        cond_winner = (
            (winners == combats_df["first_pokemon_id"])
            | (winners == combats_df["second_pokemon_id"])
        )
        invalid_winner = (~cond_winner).sum()
        
        result_null = ValidacaoResult(
            checagem="winner nulo",
            resultado=int(null_winner),
            status="OK" if null_winner == 0 else "FALHA",
        )
        
        result_invalid = ValidacaoResult(
            checagem="winner fora do par",
            resultado=int(invalid_winner),
            status="OK" if invalid_winner == 0 else "FALHA",
        )
        
        return result_null, result_invalid
    
    @staticmethod
    def validar_totais_batalhas(
        total_combats: int,
        metrics_df: pd.DataFrame,
    ) -> tuple[ValidacaoResult, ValidacaoResult]:
        """
        Valida totais de batalhas e vitórias.
            
        Retorno:
            Tuple com resultados de validação.
        """
        total_battles = int(metrics_df["total_battles"].sum())
        total_wins = int(metrics_df["total_wins"].sum())
        
        expected_battles = total_combats * 2
        expected_wins = total_combats
        
        result_battles = ValidacaoResult(
            checagem="soma total_battles",
            resultado=total_battles,
            status="OK" if total_battles == expected_battles else "FALHA",
        )
        
        result_wins = ValidacaoResult(
            checagem="soma total_wins",
            resultado=total_wins,
            status="OK" if total_wins == expected_wins else "FALHA",
        )
        
        return result_battles, result_wins
    
    @classmethod
    def validar_tudo(
        cls,
        pokemon_df: pd.DataFrame,
        combats_df: pd.DataFrame,
        metrics_df: pd.DataFrame,
    ) -> list[ValidacaoResult]:
        """
        Executa todas as validações e retorna lista de resultados.
        
        Args:
            pokemon_df: DataFrame de Pokémons.
            combats_df: DataFrame de combates.
            metrics_df: DataFrame com métricas.
            
        Retorno:
            Lista com todos os resultados de validação.
        """
        results = []
        
        res_null, res_dup = cls.validar_pokemon_ids(pokemon_df)
        results.extend([res_null, res_dup])
        
        res_winner_null, res_winner_invalid = cls.validar_combate_vencedores(combats_df)
        results.extend([res_winner_null, res_winner_invalid])
        
        res_battles, res_wins = cls.validar_totais_batalhas(len(combats_df), metrics_df)
        results.extend([res_battles, res_wins])
        
        return results
