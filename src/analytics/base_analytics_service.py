from __future__ import annotations
from typing import Sequence
import pandas as pd
from core.exceptions import ValidationError

class BaseAnalyticsService:
    @staticmethod
    def ensure_columns(
        frame: pd.DataFrame,
        required_columns: Sequence[str],
        frame_name: str,
    ) -> None:
        missing = [col for col in required_columns if col not in frame.columns]
        if missing:
            raise ValidationError(
                f"DataFrame '{frame_name}' is missing required columns: {missing}"
            )
