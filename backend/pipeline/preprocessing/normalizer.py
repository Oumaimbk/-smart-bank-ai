import re

import pandas as pd

_NOISE = re.compile(r'\b[A-Z0-9]{10,}\b|\b\d{5,}\b')


def _normalize(text: str) -> str:
    text = str(text).upper().strip()
    text = _NOISE.sub('', text)
    return re.sub(r'\s+', ' ', text).strip()


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['narration_normalized'] = df['narration'].apply(_normalize)
    return df
