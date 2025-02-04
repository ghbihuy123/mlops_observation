from ...metric_results.regression_performance import RegressionResults
from ...metric_results.regression_performance import calculate_regression_metrics
from...utils import safe_round
from typing import Optional, List, Union, Dict
from evidently.base_metric import MetricResult
from evidently.base_metric import Metric
from evidently.base_metric import InputData
from evidently.renderers.base_renderer import MetricRenderer, default_renderer
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import table_data
from evidently.model.widget import BaseWidgetInfo


class RegressionPerformanceResults(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:RegressionPerformanceResults"

    reference: Optional[RegressionResults] = None
    current: RegressionResults

class RegressionPerformanceMetrics(Metric[RegressionPerformanceResults]):
    class Config:
        type_alias = "evidently:metric:RegressionPerformanceMetrics"

    def __init__(self):
        super().__init__()

    def calculate(self, data: InputData) -> RegressionPerformanceResults:
        results = {}
        results['reference'] = None

        column_mapping = data.column_mapping
        if data.reference_data is not None:
            results['reference'] = calculate_regression_metrics(
                data.reference_data, 
                true_label_col=column_mapping.target, 
                prediction_col=column_mapping.prediction)
            
        if data.current_data is None:
            raise ValueError("The value cannot be None")

        results['current'] = calculate_regression_metrics(
                data.current_data, 
                true_label_col=column_mapping.target, 
                prediction_col=column_mapping.prediction)

        return RegressionPerformanceResults(
            reference=results['reference'],
            current=results['current']
        )




@default_renderer(wrap_type=RegressionPerformanceMetrics)
class RegressionRenders(MetricRenderer):
    def render_json(self, obj: RegressionPerformanceMetrics, include_render: bool = False,
        include: "IncludeOptions" = None, exclude: "IncludeOptions" = None,) -> dict:
        result = obj.get_result().get_dict(include_render, include, exclude)
        return result
    
    def render_html(self, obj: RegressionPerformanceMetrics) -> List[BaseWidgetInfo]:
        metric_result = obj.get_result()
        target_name = metric_result.current.target
        result = [header_text(label=f"Regression Model Performance. Target: '{target_name}’")]
        if metric_result.reference is not None:
            mae_drift = metric_result.reference.mae - metric_result.current.mae
            rmse_drift = metric_result.reference.rmse - metric_result.current.rmse
            r2_drift = metric_result.reference.r2 - metric_result.current.r2
            mape_drift = metric_result.reference.mape - metric_result.current.mape

            result.append(
                counter(
                    title="Regression Performance Drift",
                    counters=[
                        CounterData.float("MAE Drift", mae_drift, 2),
                        CounterData.float("MAPE Drift", mape_drift, 2),
                        CounterData.float("MSE Drift", rmse_drift, 2),
                        CounterData.float("R2 Score Drift", r2_drift, 2),
                    ],
                )
            )
        # ------------------------------ Table
        columns = ["","MAE", "MSE", "RMSE", "R2 Score", "MAPE"]
        values = [
            ["Current", safe_round(metric_result.current.mae, 2), safe_round(metric_result.current.mse, 2), safe_round(metric_result.current.rmse, 2), safe_round(metric_result.current.r2, 2), safe_round(metric_result.current.mape, 2)],
        ]
        if metric_result.reference is not None:
            values.append(["Reference", safe_round(metric_result.reference.mae, 2), safe_round(metric_result.reference.mse, 2), safe_round(metric_result.reference.rmse, 2), safe_round(metric_result.reference.r2, 2), safe_round(metric_result.reference.mape, 2)])
        result.append(table_data(column_names=columns, data=values))

        return result