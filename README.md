- Phiên bản Evidently: 0.4.39
- Phiên bản Python dev environment: 3.10.15


# Tổng quan về Mlops Observation

## Cấu trúc thư mục

```
├── dist/                       # Chứa file wheel đã được đóng gói thành package
├── docs/                       # Tài liệu hướng dẫn sử dụng và API
├── examples/                   # Các file ví dụ
├── notebook/                   # Chứa các Jupyter Notebook dùng cho kiểm tra và phân tích
├── reports/                    # Báo cáo kết quả kiểm tra mô hình
├── source/                     # Thư mục chính chứa mã nguồn của package
│   ├── mlops_observation/      # Thư mục chính của package
│   │   ├── calculator/         # Chứa các thuật toán tính toán metric
│   │   ├── metric_preset/      # Thiết lập các metric có sẵn
│   │   ├── metric_results/     # Lưu trữ kết quả của các metric
│   │   ├── metrics/            # Triển khai các phép đo đánh giá mô hình
│   │   ├── options/            # Cấu hình tùy chọn của mô hình
│   │   ├── renders/            # Hàm hỗ trợ vẽ đồ thị đánh giá
│   │   ├── utils/              # Chứa các hàm tiện ích
│   │   ├── __init__.py         # File khởi tạo package Python
├── test/                       # Unit test và kiểm thử
├── .gitignore
├── main.py                     # Script chính của dự án (Hiện tại chưa dùng)
├── MANIFEST.in                 # Khai báo các file cần đóng gói
├── README.md                   # Tài liệu hướng dẫn sử dụng dự án
├── requirements.txt
├── setup.py                    # Script thiết lập đóng gói package
```
# Hướng dẫn sử dụng
## Điều kiện tiên quyết
Để có thể sinh ra dashboard, điều kiện tiên quyết là cần chuẩn bị các artifact sau:
- `Reference Data` (định dạng pd.DataFrame)
- `Current Data` (định dạng pd.DataFrame, và cùng schema với Reference Data)
- `Column Mapping`: Khai báo tên các cột categorical, numerical, target, ... Ví dụ của một column mapping:
```python
from mlops_observation import ColumnMapping
# List các tên cột cho column mapping
target = 'cnt'
prediction = 'prediction'
numerical_features = ['temp', 'atemp', 'hum', 'windspeed', 'hr', 'weekday']
categorical_features = ['season', 'holiday', 'workingday']
timestamp_col = 'time_stamp'

# Truyền giá trị vào Column Mapping object
column_mapping = ColumnMapping()
column_mapping.numerical_features = numerical_features
column_mapping.categorical_features = categorical_features
column_mapping.datetime_features = timestamp_col
```
### Period Metric
Đây là các metric có cơ chế hoạt động như sau:
- Lấy tập Reference Data làm base
- Lấy tập Current Data, chia theo từng thời kỳ (ex: từng tháng, mỗi 15 ngày, từng năm, ...) thành nhiều chunks, và so sánh mỗi chunk (mỗi thời kỳ) với tập Reference Data

Hiện tại đang có:
- `PeriodDataDriftMetric`,
- `PeriodDataQualityMetric`,
- `PeriodFeatureQualityMetric`,
- `PeriodMissingValueMetric`

**Điều kiện tiên quyết**: Ta sẽ cần phải định nghĩa `column_mapping.datetime_features` để Mlops Observation có thể chia thời kỳ theo trường thời gian này
## Data Quality
- Data đầu vào là DataFrame
- Cần define list categorical features và numerical feature
- Phải có current data (reference data là optional)
### Data Quality của một bộ dữ liệu
```python
from mlops_observation import Report
from mlops_observation.metric_preset import DataQualityPreset
report = Report(metrics=[
    DataQualityPreset()
])
report.run(reference_data=None, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```
- Khi chỉ cần báo cáo data quality của một bộ dữ liệu, ta cần truyền `reference_data = None`, và truyền tập dữ liệu cần báo cáo vào `current_data`
### Data Quality so sánh hai kỳ
```python
from mlops_observation import Report
from mlops_observation.metric_preset import DataQualityPreset
report = Report(metrics=[
    DataQualityPreset()
])
report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```
- Sự khác biệt ở đây, khi ta cần so sánh hai tập dữ liệu, ta cần define `reference_data` và `current_data`

### Khi so sánh nhiều thời kỳ (theo tháng, hoặc theo tuần, ...)
Chọn reference_data làm base và sẽ chia chunk cho current_data theo trường thời gian (define trong column mapping)

```python
from mlops_observation import Report
from mlops_observation.metrics import PeriodDataQualityMetric
from mlops_observation.metrics import PeriodDataDriftMetric
from mlops_observation.metrics import PeriodFeatureQualityMetric
report = Report([
    PeriodDataQualityMetric(time_period='M'),
    PeriodFeatureQualityMetric(time_period='M')
    ])
report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
report.save_html('file_name.html')
```

## Data Drift 
- Data đầu vào là DataFrame
- Cần define list categorical features và numerical feature
- Phải có cả current và reference data

### So sánh data drift hai tập dữ liệu
```python
from mlops_observation import Report
from mlops_observation.metric_preset import DataDriftPreset
report = Report(metrics=[
    DataDriftPreset()
])
report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```

### So sánh data drift theo từng trường thời gian
```python
from mlops_observation import Report
from mlops_observation.metrics import PeriodDataQualityMetric
from mlops_observation.metrics import PeriodDataDriftMetric
from mlops_observation.metrics import PeriodFeatureQualityMetric
report = Report([
    PeriodDataDriftMetric(time_period='M'),
    ])
report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)
report.save_html('file_name.html')
```


## Model Quality 
- Phải có current data (reference data là optional)
- Data đầu vào là DataFrame
- Cần có ground truth (true label) và kết quả dự đoán
### Multi Classification
```python
from mlops_observation import Report
from mlops_observation.metric_preset import MultiClassificationPreset
report = Report(metrics=[
    MultiClassificationPreset()
])
report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```
### Binary Classification
```python
from mlops_observation import Report
from mlops_observation.metric_preset import BinaryClassificationPreset
report = Report(metrics=[
    BinaryClassificationPreset()
])
report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```
### Regression
```python
from mlops_observation import Report
from mlops_observation.metric_preset import RegressionPreset
report = Report(metrics=[
    RegressionPreset()
])
report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
report.show()
report.save_html('file_name.html')
```

# Hướng phát triển cho tương lai
- Monitor Platform (Ưu tiên)
- Concept Drift
- Multivariate Drift
- Model Performance Estimate
- Model Explain
