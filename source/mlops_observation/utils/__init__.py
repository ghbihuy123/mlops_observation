from evidently.metric_results import HistogramData

def get_small_distribution(hist_data: HistogramData):
    x = hist_data.x.to_list()
    count = hist_data.count.to_list()
    return {"x":x, 'y':count}

def safe_round(value, num_digits):
    try:
        return round(value, num_digits)
    except:
        pass

__all__ = [
    "get_small_distribution",
    "safe_round"
]