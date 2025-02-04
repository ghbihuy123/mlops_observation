from ..metrics import RegressionPerformanceMetrics
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from evidently.metric_preset.metric_preset import AnyMetric
from evidently.metric_preset.metric_preset import MetricPreset
from evidently.metrics import RegressionErrorDistribution
from evidently.metrics import RegressionErrorNormality
from evidently.metrics import RegressionErrorPlot
from evidently.utils.data_preprocessing import DataDefinition


class RegressionPreset(MetricPreset):
    class Config:
        type_alias = "evidently:metric_preset:RegressionPreset"

    """Metric preset for Regression performance analysis.

    Contains metrics:
    - RegressionQualityMetric
    - RegressionPredictedVsActualScatter
    - RegressionErrorPlot
    - RegressionErrorDistribution
    - RegressionErrorNormality
    """

    columns: Optional[List[str]]

    def __init__(self, columns: Optional[List[str]] = None):
        self.columns = columns
        super().__init__()

    def generate_metrics(
        self, data_definition: DataDefinition, additional_data: Optional[Dict[str, Any]]
    ) -> List[AnyMetric]:
        return [
            RegressionPerformanceMetrics(),
            RegressionErrorPlot(),
            RegressionErrorDistribution(),
            RegressionErrorNormality(),
        ]