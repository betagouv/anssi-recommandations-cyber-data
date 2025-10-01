from typing import NamedTuple, Dict, List


class DatasetReponse(NamedTuple):
    name: str
    readme: str
    default_metric: str
    columns_map: Dict[str, str]
    id: int
    created_at: str
    size: int
    columns: List[str]
    parquet_size: int
    parquet_columns: List[str]


DATASET_REPONSE_VIDE = DatasetReponse(
    name="",
    readme="",
    default_metric="",
    columns_map={},
    id=-1,
    created_at="",
    size=0,
    columns=[],
    parquet_size=0,
    parquet_columns=[],
)
