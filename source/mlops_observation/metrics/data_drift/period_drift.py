from ...utils.data_drift import convert_test_period_into_dataframe
from ...metric_results.data_drift.feature_drift_period import calculate_test_in_period
from ...utils.data_drift import convert_test_period_into_dataframe
from ...utils.visualization import drift_combine_plot
from ...utils.visualization import dataframe_to_widget
from ...utils.visualization import plot_drift_distribution
from ...utils.visualization import period_categorical_distribution_drift
from ...utils.data_drift import calculate_period_drifted_dict
from ...utils.data_operations import divide_into_chunks_by_period
from ...options.color_scheme import ColorOptions
from ...renders.base_renders import MetricRenderer
from ...metric_results.data_drift.feature_drift_period import DriftPeriodResult
from typing import Optional
from typing import Dict
from typing import List
from evidently.renderers.base_renderer import default_renderer
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.base_metric import InputData
from evidently.renderers.base_renderer import MetricRenderer, default_renderer
from evidently.model.widget import BaseWidgetInfo
from evidently.renderers.html_widgets import ColumnDefinition
from evidently.renderers.html_widgets import RichTableDataRow
from evidently.renderers.html_widgets import RowDetails
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import plotly_figure
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import counter
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import CounterData
import plotly.graph_objects as go

class PeriodDataDrifts(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:PeriodDataDrifts"
    feature_period_plots: Optional[Dict[str, DriftPeriodResult]]
    reference_date_list: list
    current_date_list: list
class PeriodDataDriftMetric(Metric[PeriodDataDrifts]):
    """
    time_period (str): Offset aliases https://pandas.pydata.org/docs/user_guide/timeseries.html#dateoffset-objects
    """
    class Config:
        type_alias = "evidently:metric:PeriodDataDriftMetric"
    _time_period: str
    def __init__(self, time_period: str = 'M'):
        self._time_period = time_period
        super().__init__()
    def calculate(self, data: InputData):
        if data.reference_data is None:
            raise ValueError("Reference dataset should be present")
        if data.current_data is None:
            raise ValueError("Current dataset should be present")
            
        result = {}
        column_mapping = data.column_mapping

        reference_chunks = divide_into_chunks_by_period(
            data=data.reference_data,
            time_column=column_mapping.datetime_features,
            period = self._time_period
        )

        current_chunks = divide_into_chunks_by_period(
            data=data.current_data,
            time_column=column_mapping.datetime_features,
            period = self._time_period
        )

        if column_mapping.categorical_features is not None:
            for cat_col in column_mapping.categorical_features:
                # try:
                #     distribution_figure = period_categorical_distribution_drift(
                #         reference=data.reference_data,
                #         current=data.current_data,
                #         col_name=cat_col,
                #         timestamp_col=column_mapping.datetime_features,
                #         chunk_period=self._time_period
                #     )
                # except:
                #     print(f'Joyplot distribution at {cat_col} unsuccessiful (could be affected by OverflowError: Python int too large to convert to C long or other error)')
                #     distribution_figure = go.Figure()
                distribution_figure, stat_result = period_categorical_distribution_drift(
                    reference=data.reference_data,
                    current=data.current_data,
                    current_chunks=current_chunks,
                    col_name=cat_col,
                    timestamp_col=column_mapping.datetime_features,
                    chunk_period=self._time_period
                )
                
                # stat_result = calculate_test_in_period(
                #     reference=data.reference_data,
                #     current_chunks=current_chunks,
                #     col_name=cat_col,
                #     col_type='cat',
                # )
                # -----------------------------------
                reference_date_list, current_date_list, current_drifted = calculate_period_drifted_dict(
                    reference=data.reference_data,
                    timestamp_col=column_mapping.datetime_features,
                    period_stat_result=stat_result
                )
                period_drifted_count = sum(current_drifted)
                period_count = len(current_date_list)
                # -----------------------------------
                drift_figure = drift_combine_plot(stat_result)
                stat_table = convert_test_period_into_dataframe(stat_result) \
                    .reset_index() \
                    .rename({'index': ''}, axis=1)
                result[cat_col] = DriftPeriodResult(
                    distribution=distribution_figure,
                    drift_period=drift_figure,
                    col_type='cat',
                    col_name=cat_col,
                    stat_table=stat_table,
                    period_drifted_count=period_drifted_count,
                    period_count=period_count
                )
            
        if column_mapping.numerical_features is not None:
            for num_col in column_mapping.numerical_features:
                distribution_figure=go.Figure()
                stat_result = calculate_test_in_period(
                    reference=data.reference_data,
                    current_chunks=current_chunks,
                    col_name=num_col,
                    col_type='num'
                )
                # -------------------------------------
                reference_date_list, current_date_list, current_drifted = calculate_period_drifted_dict(
                    reference=data.reference_data,
                    timestamp_col=column_mapping.datetime_features,
                    period_stat_result=stat_result
                )
                period_drifted_count = sum(current_drifted)
                period_count = len(current_date_list)
                # -------------------------------------
                drift_figure = drift_combine_plot(stat_result)
                stat_table = convert_test_period_into_dataframe(stat_result) \
                    .reset_index() \
                    .rename({'index': ''}, axis=1)

                distribution_figure = plot_drift_distribution(
                    reference_chunks=reference_chunks, 
                    current_chunks=current_chunks, 
                    col_name=num_col, 
                    current_date_list=current_date_list, 
                    current_drifted=current_drifted
                )

                result[num_col] = DriftPeriodResult(
                    distribution=distribution_figure,
                    drift_period=drift_figure,
                    col_type='num',
                    col_name=num_col,
                    stat_table=stat_table,
                    period_drifted_count=period_drifted_count,
                    period_count=period_count
                )
        return PeriodDataDrifts(
            feature_period_plots=result, 
            current_date_list=current_date_list, 
            reference_date_list=reference_date_list
            )

@default_renderer(wrap_type=PeriodDataDriftMetric)
class DataDriftRender(MetricRenderer):
    def _generate_column_params(
        self,
        column_data: DriftPeriodResult
        )-> Optional[RichTableDataRow]:
        details = RowDetails()
        # -----------------------------------------
        table = column_data.stat_table
        table = dataframe_to_widget(table)
        details.with_part("STAT TABLE", info=table)
        # -----------------------------------------
        dist_fig = column_data.distribution
        dist_fig = plotly_figure(title='', figure=dist_fig)
        details.with_part("DISTRIBUTION", info=dist_fig)
        # -----------------------------------------
        drift_fig = column_data.drift_period
        drift_fig = plotly_figure(title='', figure=drift_fig)
        details.with_part("DRIFT", info=drift_fig)
        # -----------------------------------------
        
        return RichTableDataRow({
            "column_name": column_data.col_name, 
            "column_type": column_data.col_type,
            "period_drifted_count": fr"{column_data.period_drifted_count}/{column_data.period_count}"
            }, 
            details=details)
        
    def render_html(self, obj: PeriodDataDriftMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        data=[]
        counters = [
            CounterData.string(f"{results.reference_date_list[0]} to {results.reference_date_list[-1]}", 'Reference'),
            CounterData.string(f"{results.current_date_list[0]} to {results.current_date_list[-1]}", "Current")
        ]
        columns = [
            ColumnDefinition("Column Name", "column_name"),
            ColumnDefinition("Type", "column_type"),
            ColumnDefinition("Number of drifted periods", "period_drifted_count")
        ]
        for col in results.feature_period_plots.keys():
            column_data = results.feature_period_plots[col]
            param = self._generate_column_params(
                    column_data=column_data
            )
            data.append(param)
        return [
            header_text(label=f"Period Drift Report"),
            counter(counters=counters),
            rich_table_data(
                title="",
                columns=columns,
                data=data
            )
        ]