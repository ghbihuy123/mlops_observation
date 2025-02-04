from evidently.metric_results import MetricResult
import pandas as pd
from typing import Optional
from typing import List
from typing import Sequence
from typing import Union
from typing import Dict
class DatasetUtilityColumns(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:DatasetUtilityColumns"

    date: Optional[str]
    id: Optional[str]
    target: Optional[str]
    prediction: Optional[Union[str, Sequence[str]]]

TargetNames = Union[List[Union[int, str]], Dict[Union[int, str], str]]


class DatasetColumns(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:DatasetColumns"
        dict_exclude_fields = {"task", "target_type"}
        pd_include = False
    utility_columns: DatasetUtilityColumns
    target_type: Optional[str]
    num_feature_names: List[str]
    cat_feature_names: List[str]
    text_feature_names: List[str]
    target_names: Optional[TargetNames]
    task: Optional[str]
    @property
    def target_names_list(self) -> Optional[List]:
        if isinstance(self.target_names, dict):
            return list(self.target_names.keys())
        return self.target_names


class DatasetSummary:
    def __init__(
        self,
        number_of_columns: int,
        number_of_rows: int,
        number_of_missing_values: int,
        number_of_categorical_columns: int,
        number_of_numeric_columns: int,
        number_of_text_columns: int,
        number_of_constant_columns: int,
        number_of_almost_constant_columns: int,
        number_of_duplicated_columns: int,
        number_of_almost_duplicated_columns: int,
        number_of_empty_rows: int,
        number_of_empty_columns: int,
        number_of_duplicated_rows: int,
        nans_by_columns: Dict[str, int],
        number_uniques_by_columns: Dict[str, int],
    ):
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows
        self.number_of_missing_values = number_of_missing_values
        self.number_of_categorical_columns = number_of_categorical_columns
        self.number_of_numeric_columns = number_of_numeric_columns
        self.number_of_text_columns = number_of_text_columns
        self.number_of_constant_columns = number_of_constant_columns
        self.number_of_almost_constant_columns = number_of_almost_constant_columns
        self.number_of_duplicated_columns = number_of_duplicated_columns
        self.number_of_almost_duplicated_columns = number_of_almost_duplicated_columns
        self.number_of_empty_rows = number_of_empty_rows
        self.number_of_empty_columns = number_of_empty_columns
        self.number_of_duplicated_rows = number_of_duplicated_rows
        self.nans_by_columns = nans_by_columns
        self.number_uniques_by_columns = number_uniques_by_columns
    def __repr__(self):
        return (
            f"DatasetSummary("
            f"number_of_columns={self.number_of_columns}, number_of_rows={self.number_of_rows}, "
            f"number_of_missing_values={self.number_of_missing_values}, "
            f"number_of_categorical_columns={self.number_of_categorical_columns}, "
            f"number_of_numeric_columns={self.number_of_numeric_columns}, "
            f"number_of_text_columns={self.number_of_text_columns}, "
            f"number_of_constant_columns={self.number_of_constant_columns}, "
            f"number_of_almost_constant_columns={self.number_of_almost_constant_columns}, "
            f"number_of_duplicated_columns={self.number_of_duplicated_columns}, "
            f"number_of_almost_duplicated_columns={self.number_of_almost_duplicated_columns}, "
            f"number_of_empty_rows={self.number_of_empty_rows}, number_of_empty_columns={self.number_of_empty_columns}, "
            f"number_of_duplicated_rows={self.number_of_duplicated_rows}, "
            f"nans_by_columns={self.nans_by_columns}, number_uniques_by_columns={self.number_uniques_by_columns})"
        )


