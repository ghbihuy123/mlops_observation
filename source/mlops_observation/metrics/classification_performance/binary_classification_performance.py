import pandas as pd
from typing import Optional, Dict
from evidently.calculations.classification_performance import get_prediction_data
from evidently.renderers.base_renderer import MetricRenderer, default_renderer
from evidently.base_metric import InputData, Metric, MetricResult
from evidently.utils.data_operations import process_columns
from evidently import ColumnMapping
from evidently.base_metric import Metric
from ...metric_results.classification.classification_calculator import calculate_classification_results
from ...metric_results.classification.classification_calculator import ClassificationResult
class BinaryClassificationPerformanceResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:BinaryClassificationPerformanceResult"
    reference: Optional[ClassificationResult]
    current: ClassificationResult

class BinaryClassificationPerformanceMetric(Metric[ClassificationResult]):
    class Config:
        type_alias = "evidently:metric:BinaryClassificationPerformanceMetric"
    _threshold: float
    def __init__(self, threshold: float = 0.5):
        self._threshold = threshold
        super().__init__()

    def calculate(self, data: InputData) -> ClassificationResult:
        results = {}
        results['reference'] = None
        if data.current_data is None:
            raise ValueError("The value cannot be None")

        if data.reference_data is not None:
            results['reference'] = self.get_classification_result(data.reference_data, data.column_mapping)

        results['current'] = self.get_classification_result(data.current_data, data.column_mapping)
        return BinaryClassificationPerformanceResult(
            reference=results['reference'],
            current=results['current']
        )
        
    def get_classification_result(self, data: pd.DataFrame, column_mapping: ColumnMapping) -> ClassificationResult:
        
        dataset_column = process_columns(data, column_mapping)
        prediction_data = get_prediction_data(data, data_columns=dataset_column, pos_label=None, threshold=self._threshold)
        results = calculate_classification_results(
            prediction=prediction_data.predictions,
            target=data[dataset_column.utility_columns.target],
            prediction_proba=prediction_data.prediction_probas[column_mapping.pos_label]
        )
        return results


@default_renderer(wrap_type=BinaryClassificationPerformanceMetric)
class BinaryClassificationPerformanceRender(MetricRenderer):
    def render_json(self, obj: BinaryClassificationPerformanceMetric, include_render: bool = False,
        include: "IncludeOptions" = None, exclude: "IncludeOptions" = None,) -> dict:
        result = obj.get_result().get_dict(include_render, include, exclude)
        return result