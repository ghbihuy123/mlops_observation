from ...utils import get_small_distribution
from ...utils import safe_round
from ...metric_results.data_drift import CategoricalFeatureDrift
from ...metric_results.data_drift import get_one_categorical_column_drift
from ...metric_results.data_drift import NumericFeatureDrift
from ...metric_results.data_drift import get_one_numeric_column_drift

from typing import Optional, Dict, List
from typing import Union
from evidently.renderers.base_renderer import MetricRenderer, default_renderer
from evidently.model.widget import BaseWidgetInfo
from evidently.base_metric import InputData, Metric, MetricResult
from evidently.utils.data_operations import process_columns
from evidently import ColumnMapping

from evidently.renderers.html_widgets import ColumnDefinition
from evidently.renderers.html_widgets import RichTableDataRow
from evidently.renderers.html_widgets import RowDetails
from evidently.renderers.html_widgets import CounterData
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import table_data
from evidently.renderers.html_widgets import counter
from evidently.utils.visualizations import plot_distr
from evidently.renderers import html_widgets


class DataDriftCalculate(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:DataDriftResult"
    numeric_results: Optional[Dict[str, NumericFeatureDrift]]
    categorical_results: Optional[Dict[str, CategoricalFeatureDrift]]
    number_of_columns: int
    number_of_drifted: int


class DataDriftMetric(Metric[DataDriftCalculate]):
    class Config:
        type_alias = "evidently:metric:DataDriftMetric"

    def __init__(self):
        super().__init__()

    def calculate(self, data: InputData):
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")
        if data.current_data is None:
            raise ValueError("Current dataset should be present")

        column_mapping = data.column_mapping
        categorical_results = {}
        numeric_results = {}
        number_of_columns = 0
        number_of_drifted = 0

        if column_mapping.categorical_features:
            number_of_columns += len(column_mapping.categorical_features)
            for column in column_mapping.categorical_features:
                categorical_metrics = get_one_categorical_column_drift(
                    current=data.current_data,
                    reference=data.reference_data,
                    column_name=column
                )
                if categorical_metrics.drifted:
                    number_of_drifted += 1
                categorical_results[column] = categorical_metrics
        
        if column_mapping.numerical_features:
            number_of_columns += len(column_mapping.numerical_features)
            for column in column_mapping.numerical_features:
                numeric_metrics = get_one_numeric_column_drift(
                    current=data.current_data,
                    reference=data.reference_data,
                    column_name=column
                )
                if numeric_metrics.drifted:
                    number_of_drifted += 1
                numeric_results[column] = numeric_metrics


        return DataDriftCalculate(
            numeric_results=numeric_results,
            categorical_results=categorical_results,
            number_of_columns=number_of_columns,
            number_of_drifted=number_of_drifted
        )


@default_renderer(wrap_type=DataDriftMetric)
class DataDriftRender(MetricRenderer):
    def render_json(self, obj: DataDriftMetric, include_render: bool = False,
        include: "IncludeOptions" = None, exclude: "IncludeOptions" = None,) -> dict:
        result = obj.get_result().get_dict(include_render, include, exclude)
        return result
    
    def _generate_column_params(
        self,
        column_data: Union[NumericFeatureDrift, CategoricalFeatureDrift],
        column_type: str
        )-> Optional[RichTableDataRow]:
        
        details = RowDetails()
        # -----------------------------------------
        drift_columns = ["Stattest Name", "Drift Score", 'Drift Detect']
        if column_type == 'num':
            values = [
                ["Jensen Shanon Divergence", safe_round(column_data.jensen_shanon_divergence.drift_score, 7), 'Detect' if column_data.jensen_shanon_divergence.drifted else 'No'],
                ["Wasserstein Distance Norm", safe_round(column_data.wasserstein_distance_norm.drift_score, 7), 'Detect' if column_data.wasserstein_distance_norm.drifted else 'No'],
                ["Kolmogorov Smirnov", safe_round(column_data.kolmogorov_smirnov.drift_score, 7), 'Detect' if column_data.kolmogorov_smirnov.drifted else 'No'],
            ]
        if column_type == 'cat':
            values = [
                ["PSI", safe_round(column_data.psi.drift_score, 7), 'Detect' if column_data.psi.drifted else 'No'],
                ["Chi Square", safe_round(column_data.chi_square.drift_score, 7), 'Detect' if column_data.chi_square.drifted else 'No'],
                ["Cramer", safe_round(column_data.cramer.drift_score, 7), 'Detect' if column_data.cramer.drifted else 'No'],
            ]
        drift_table2 = table_data(column_names=drift_columns, data=values)
        details.with_part("DRIFT CALCULATORS", info=drift_table2)
        # ----------------------------------------
        
        fig = plot_distr(
            hist_curr=column_data.hist_data.current, 
            hist_ref=column_data.hist_data.reference, 
            color_options=self.color_options)
        hist = plotly_figure(title='', figure=fig)
        details.with_part("DISTRIBUTION", info=hist)
        
        current_distribution = column_data.hist_data.current
        reference_distribution = column_data.hist_data.reference
        # -------------------------
        return RichTableDataRow({
            "column_name": column_data.column_name, 
            "column_type": column_data.column_type,
            "current_distribution": get_small_distribution(current_distribution),
            "reference_distribution": get_small_distribution(reference_distribution),
            "drift_detect": "Detect" if column_data.drifted else "No"
            }, 
            details=details)
        

    def render_html(self, obj: DataDriftMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options

        number_drifted_percent = results.number_of_drifted / results.number_of_columns * 100
        counters = [
            CounterData.int("Columns", results.number_of_columns),
            CounterData.int("Drifted Columns", results.number_of_drifted),
            CounterData.float("Drifted Columns Proportion", number_drifted_percent / 100, 2),
        ]
        
        columns = [
            ColumnDefinition("Column Name", "column_name"),
            ColumnDefinition("Type", "column_type"),
            ColumnDefinition(
                "Reference Distribution",
                "reference_distribution",
                html_widgets.ColumnType.HISTOGRAM,
                options={
                    "xField": "x",
                    "yField": "y",
                    "color": color_options.primary_color,
                },
            ),
            ColumnDefinition(
                "Current Distribution",
                "current_distribution",
                html_widgets.ColumnType.HISTOGRAM,
                options={
                    "xField": "x",
                    "yField": "y",
                    "color": color_options.primary_color,
                },
            ),
            ColumnDefinition("Drift Detect", "drift_detect"),
        ]
        data = []
        for col in results.categorical_results.keys():
            column_data = results.categorical_results[col]
            param = self._generate_column_params(
                    column_data=column_data, 
                    column_type='cat'
            )
            data.append(param)
        for col in results.numeric_results.keys():
            column_data = results.numeric_results[col]
            param = self._generate_column_params(
                    column_data=column_data, 
                    column_type='num'
            )
            data.append(param)
        
        
        return [
            header_text(label="Data Drift Summary"),
            counter(
                counters=counters,
                title="",
            ),
            rich_table_data(
                title=f"Drift is detected for {number_drifted_percent:.2f}% of columns "
                f"({results.number_of_drifted} out of {results.number_of_columns})."
                ,
                columns=columns,
                data=data
            )
        ]
