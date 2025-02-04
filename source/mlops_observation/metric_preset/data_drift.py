from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.metric_preset.metric_preset import AnyMetric
from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import ColumnSummaryMetric
from evidently.metrics import DatasetSummaryMetric
from evidently.metrics.base_metric import generate_column_metrics
from evidently.metrics.data_integrity.dataset_missing_values_metric import DatasetMissingValuesMetric
from evidently.utils.data_preprocessing import DataDefinition
from ..metrics import DataDriftMetric

class DataDriftPreset(MetricPreset):
    class Config:
        type_alias = "evidently:metric_preset:DataDriftPreset"

    """Metric preset for Data Drift analysis.

    Contains metrics:
    - DataDriftMetric

    Args:
        columns: list of columns for analysis.
    """

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None):
        self.columns = columns
        super().__init__()

    def generate_metrics(
        self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]
    ) -> List[AnyMetric]:
        return [
            DataDriftMetric()
        ]