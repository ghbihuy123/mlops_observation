# from ..metric_results.data_drift.feature_drift_period import calculate_test_in_period
from ..options import ColorOptions
from .data_drift import calculate_period_drifted_dict
from ..metric_results.data_drift import CategoricalFeatureDrift
from ..metric_results.data_drift import NumericFeatureDrift
from nannyml.drift.univariate import UnivariateDriftCalculator
import plotly.graph_objects as go
from typing import Union
from typing import List
from typing import Dict
from typing import Literal
import pandas as pd
from nannyml.distribution import ContinuousDistributionCalculator
from nannyml.distribution import CategoricalDistributionCalculator
import warnings
from evidently.renderers.html_widgets import WidgetSize, BaseWidgetInfo
from evidently.renderers.html_widgets import table_data

# Suppress all warnings
warnings.filterwarnings("ignore")

def period_distribution_num_plot(
    reference: pd.DataFrame, 
    current: pd.DataFrame, 
    col: str, 
    timestamp_col: str,
    color_option: ColorOptions = ColorOptions(),
    chunk_period: str = "M",
) -> go.Figure:
    # if col_type == 'num':
    continuous_dist = ContinuousDistributionCalculator(
    column_names=col,
    timestamp_column_name = timestamp_col,
    chunk_period=chunk_period,
    )
    fig = continuous_dist.fit(reference) \
        .calculate(current) \
        .filter(period='all', column_names=col) \
        .plot(kind='distribution')

    found_analysis = False
    for trace in fig.data:  
        if 'x' in trace:
            trace['x'] = pd.to_datetime(trace['x'], errors='coerce')  # Convert x values to datetime

        if trace.name == "Reference":
            trace.line.color = color_option.secondary_gradient_color[0]

        if trace.name == "Analysis":  # Check if the trace name is "Analysis"
            trace.line.color = color_option.primary_gradient_color[0]  # Update the color to red
            found_analysis = True
        
        if found_analysis == True and isinstance(trace, go.Scatter) and trace.fill =='tonexty':
            trace.fillcolor = color_option.primary_gradient_color[1]
        else:
            trace.fillcolor = color_option.secondary_gradient_color[1]


    bg_color = fig.layout.plot_bgcolor or fig.layout.paper_bgcolor
    axis_line_color = 'white' if bg_color in ['black', '#000000', '#111111'] else 'black'
    fig.update_layout(
        xaxis=dict(
            type="date",
            title="Time",
            showline=True,
            linecolor=axis_line_color,
        ),
        yaxis=dict(
            title="Value",
            showline=True,
            linecolor=axis_line_color,
        ),
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def period_distribution_cat_plot(
    reference: pd.DataFrame, 
    current: pd.DataFrame, 
    col: str, 
    timestamp_col: str,
    color_option: ColorOptions = ColorOptions(),
    chunk_period: str = "M",
) -> go.Figure:
    categorical_dist = CategoricalDistributionCalculator(
        column_names=col,
        timestamp_column_name = timestamp_col,
        chunk_period=chunk_period,
    )
    fig = categorical_dist.fit(reference) \
        .calculate(current) \
        .filter(period='all', column_names=col) \
        .plot(kind='distribution')
    bg_color = fig.layout.plot_bgcolor or fig.layout.paper_bgcolor
    axis_line_color = 'white' if bg_color in ['black', '#000000', '#111111'] else 'black'
    fig.update_layout(
    xaxis=dict(
        type="date",
        title="Time",
        showline=True,
        linecolor=axis_line_color,
    ),
    yaxis=dict(
        title="Value",
        showline=True,
        linecolor=axis_line_color,
    ),
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig



def combine_fig(figures: List[go.Figure], button_names: List[str]) -> go.Figure:
    """
    Combines multiple Plotly figures into a single figure with buttons to toggle between them.

    Args:
        figures (List[go.Figure]): A list of Plotly figure objects to combine.
        button_names (List[str]): A list of names for the buttons corresponding to each figure.

    Returns:
        go.Figure: A combined Plotly figure with buttons for toggling between the input figures.
    """
    combined_fig = go.Figure()

    # Validate inputs
    if len(figures) != len(button_names):
        raise ValueError("The number of figures must match the number of button names.")

    # Add all traces from each figure to the combined figure
    for fig in figures:
        combined_fig.add_traces(fig.data)

    # Create visibility settings for each button
    num_traces = [len(fig.data) for fig in figures]
    visibility_list = []
    for i, count in enumerate(num_traces):
        visibility = [False] * sum(num_traces)
        start = sum(num_traces[:i])
        visibility[start:start + count] = [True] * count
        visibility_list.append(visibility)

    # Initially set only the first figure visible
    for i, trace in enumerate(combined_fig.data):
        trace.visible = visibility_list[0][i]

    # Define buttons to toggle between figures
    buttons = []
    for i, (visibility, name, fig) in enumerate(zip(visibility_list, button_names, figures)):
        buttons.append(
            dict(
                label=name,
                method="update",
                args=[
                    {"visible": visibility},  # Update visibility
                    fig.layout.to_plotly_json()  # Apply layout of the current figure
                ]
            )
        )

    # Add buttons to the layout
    combined_fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=1,
                y=1.2,
                buttons=buttons
            )
        ]
    )

    # Set the initial state to show the first figure
    combined_fig.update_layout(figures[0].layout.to_plotly_json())

    return combined_fig





def dataframe_to_widget(data: pd.DataFrame, title: str = "", size: WidgetSize = WidgetSize.FULL) -> BaseWidgetInfo:
    """
    Convert a pandas DataFrame to a BaseWidgetInfo object for displaying as a table.

    Args:
        data: The pandas DataFrame to be converted.
        title: The title of the widget.
        size: The widget size (default is WidgetSize.FULL).

    Returns:
        BaseWidgetInfo: The widget information object with table data.
    """
    # Extract column names and data from DataFrame
    column_names = data.columns.tolist()
    rows = data.values.tolist()

    # Generate the table widget using the `table_data` function
    return table_data(column_names=column_names, data=rows, title=title, size=size)

def period_numerical_distribution_drift(
    reference: pd.DataFrame, 
    current: pd.DataFrame, 
    col_name: str, 
    timestamp_col: str, 
    chunk_period: str = 'M', 
    color_options: ColorOptions = ColorOptions()
    ) -> go.Figure:
    from ..metric_results.data_drift.feature_drift_period import calculate_test_in_period

    drift_results = calculate_test_in_period(reference, current, col_name, timestamp_col, col_type='num', chunk_period=chunk_period)
    reference_date_list, current_date_list, current_drifted_list = calculate_period_drifted_dict(reference, timestamp_col, drift_results)
    fig = period_distribution_num_plot(
        reference=reference,
        current=current,
        col=col_name,
        timestamp_col=timestamp_col,
        chunk_period=chunk_period
    )
    num_traces = 5
    len_reference_period = len(reference_date_list)
    len_current_period = len(current_date_list)

    for i in range(len_reference_period):
        pivot_index = i*num_traces
        fig.data[pivot_index].line.color = color_options.primary_gradient_color[0]
        fig.data[pivot_index+1].fillcolor = color_options.primary_gradient_color[1]
        fig.data[pivot_index+2].line.color = color_options.primary_gradient_color[0]
        fig.data[pivot_index+3].line.color = color_options.primary_gradient_color[0]
        fig.data[pivot_index+4].line.color = color_options.primary_gradient_color[0]
    for i in range(len_reference_period, len_reference_period + len_current_period):
        pivot_index = i*num_traces
        if current_drifted_list[i-len_reference_period]:
            color = color_options.drifted_gradient_color[0]
            transparent_color = color_options.drifted_gradient_color[1]
        else:
            color = color_options.secondary_gradient_color[0]
            transparent_color = color_options.secondary_gradient_color[1]
        fig.data[pivot_index].line.color = color
        fig.data[pivot_index+1].fillcolor = transparent_color
        fig.data[pivot_index+2].line.color = color
        fig.data[pivot_index+3].line.color = color
        fig.data[pivot_index+4].line.color = color
    return fig

def period_categorical_distribution_drift(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    current_chunks: Dict[str, pd.DataFrame],
    col_name: str,
    timestamp_col: str,
    chunk_period: str = 'M', 
    color_options: ColorOptions = ColorOptions()
    ):
    from ..metric_results.data_drift.feature_drift_period import calculate_test_in_period
    from .data_operations import divide_into_chunks_by_period
    # print(current_chunks)
    drift_results = calculate_test_in_period(reference, current_chunks, col_name, col_type='cat')
    _, _, current_drifted_list = calculate_period_drifted_dict(reference, timestamp_col, drift_results)
    fig = period_distribution_cat_plot(
        reference=reference,
        current=current,
        col=col_name,
        timestamp_col=timestamp_col,
        chunk_period=chunk_period
    )
    len_data = len(fig.data)
    drifted_color = []
    # print(drift_results)
    for is_drift in current_drifted_list:
        if is_drift:
            drifted_color.append('red')
        else:
            drifted_color.append('rgba(0,0,0,0)')
    for i in range(int(len_data/2), len_data):
        fig.data[i].marker.line.color = drifted_color
        fig.data[i].marker.line.width = 1.5
    return fig, drift_results

def stattest_periods_plot(
    stattest_result: Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]],
    color_option: ColorOptions = ColorOptions(),
    num_test_method: str = None,
    cat_test_method: str = None
) -> go.Figure:
    """
    Generate a scatter plot with a line for statistical test results over periods.

    Args:
        stattest_result: A dictionary containing test results over time.
        color_option: An instance of ColorOptions to define plot colors.
        num_test_method: Numerical test method to be used.
            - `wasserstein_distance_norm`
            - `kolmogorov_smirnov`
            - `jensen_shanon_divergence`
        cat_test_method: Categorical test method to be used (e.g., 'psi').
            - `psi`
            - `chi_square`
            - `cramer`

    Returns:
        A Plotly Figure with the plot of the selected test method.
    """
    if not num_test_method and not cat_test_method:
        raise ValueError("At least one of num_test_method or cat_test_method must be provided.")
    
    # Select test method
    test_method = num_test_method if num_test_method else cat_test_method
    name_map = {
        'psi': 'PSI',
        'chi_square': 'Chi Square',
        'cramer': "Cramer'V",
        'wasserstein_distance_norm': 'Wasserstein Distance Norm',
        'kolmogorov_smirnov': 'Kolmogorov Smirnov',
        'jensen_shanon_divergence': 'Jensen Shanon Divergence',
    }
    # Extract data for the selected test method
    periods = []
    scores = []
    thresholds = []
    drifted_points = {
        "x": [],
        "y": []
    }

    for period, result in stattest_result.items():
        # Check if the test method exists in the object
        if hasattr(result, test_method):
            stat_result = getattr(result, test_method)
            if stat_result is not None:
                periods.append(period)
                scores.append(stat_result.drift_score)
                thresholds.append(stat_result.actual_threshold)
                if stat_result.drifted:
                    drifted_points["x"].append(period)
                    drifted_points["y"].append(stat_result.drift_score)

    # Create the figure
    fig = go.Figure()

    # Add the line and scatter plot for the drift scores
    fig.add_trace(go.Scatter(
        x=periods,
        y=scores,
        mode='lines+markers',
        name='Drift Scores',
        line=dict(color=color_option.secondary_gradient_color[0])
    ))

    # Add the threshold as a dashed line
    fig.add_trace(go.Scatter(
        x=periods,
        y=thresholds,
        mode='lines',
        name='Threshold',
        line=dict(color='RED', dash='dot')
    ))

    # Highlight drifted points in red (grouped into a single trace)
    if drifted_points["x"]:
        fig.add_trace(go.Scatter(
            x=drifted_points["x"],
            y=drifted_points["y"],
            mode='markers',
            name='Drifted Points',
            marker=dict(color=color_option.primary_color, size=7, symbol='circle')
        ))
    bg_color = fig.layout.plot_bgcolor or fig.layout.paper_bgcolor
    axis_line_color = 'white' if bg_color in ['black', '#000000', '#111111'] else 'black'
    # Update layout
    fig.update_layout(
        title=f"Statistical Test {name_map[test_method]}",
        xaxis=dict(
            type="date",
            title="Time",
            showline=True,
            linecolor=axis_line_color,
            showgrid=False
        ),
        yaxis=dict(
            title="Value",
            showline=True,
            linecolor=axis_line_color,
            showgrid=False,
            zeroline=False
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def drift_combine_plot(
    stattest_result: Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]]
    ) -> go.Figure:
    col_type = stattest_result[sorted(stattest_result.keys())[0]].column_type
    if col_type == 'numeric':
        methods = ['wasserstein_distance_norm', 'kolmogorov_smirnov', 'jensen_shanon_divergence', 'psi']
    elif col_type == 'categorical':
        methods = ['cramer', 'psi', 'chi_square']
    else:
        raise ValueError("col_type must be defined as 'num' or 'cat'")
    figure_list = []
    for method in methods:
        figure_list.append(
            stattest_periods_plot(stattest_result, cat_test_method=method, color_option=ColorOptions())
    )
    fig = combine_fig(figures=figure_list, button_names=methods)
    return fig

def plot_drift_distribution(
    reference_chunks: Dict[str, pd.DataFrame],
    current_chunks: Dict[str, pd.DataFrame],
    col_name: str,
    current_date_list: List[str],
    current_drifted: List[bool],
    colors_options: ColorOptions = ColorOptions()
    ):
    def _drift_date_dict(
        current_date_list: List[str],
        current_drifted: List[bool]
        ):
        drift_dict = {}
        for i in range(len(current_date_list)):
            drift_dict[current_date_list[i]] = current_drifted[i]
        return drift_dict

    data = []
    date_keys = []
    drift_dict = {}

    for key in reference_chunks.keys():
        data.append(reference_chunks[key][col_name])
        date_keys.append(key)

    for key in current_chunks.keys():
        data.append(current_chunks[key][col_name])
        date_keys.append(key)
        
    drift_dict = _drift_date_dict(current_date_list, current_drifted)
    fig = go.Figure()

    # Plot rotated violins for each date key
    for i, (date_key, data_line) in enumerate(zip(date_keys, data)):
        if date_key in reference_chunks.keys():
            color = colors_options.primary_gradient_color[0]
        elif drift_dict[date_key]:
            color = colors_options.drifted_gradient_color[0]
        else:
            color = colors_options.secondary_gradient_color[0]

        fig.add_trace(
            go.Violin(
                x=[date_key] * len(data_line),
                y=data_line,
                side='negative',
                width=1.8,
                points=False,
                line=dict(color=color, width=0.5),
                name=date_key,
                meanline_visible=True,
                showlegend=False
            ))

        fig.update_layout(
            title=f"Distribution In Period of '{col_name}'",
            xaxis_title="Time Periods",
            yaxis_title="Value",
            xaxis=dict(
                type="category",
                tickmode="array",
                tickvals=date_keys,
                ticktext=date_keys,
                showgrid=False,
                zeroline=False,
                linecolor='black',  # Set outer frame color for x-axis
                linewidth=0.8,  # Set outer frame line width for x-axis
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False,
                linecolor='black',  # Set outer frame color for x-axis
                linewidth=0.8,  # Set outer frame line width for x-axis
            ),
            violingap=0,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
    return fig