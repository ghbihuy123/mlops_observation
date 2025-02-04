from .confusion_matrix import calculate_confusion_matrix_by_classes
from ...calculator.classification_performance import calculate_confusion_by_classes 

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import roc_auc_score
from sklearn.metrics import log_loss
from sklearn.metrics import confusion_matrix


from typing import Optional, Union
from evidently.base_metric import MetricResult, InputData

class ClassificationResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:MultiClassificationResult"
    accuracy: float
    confusion_matrix: dict
    classification_info: dict
    logloss: Optional[float]
    roc_auc: Optional[dict]
    mattheus_corr_coefficient:  Optional[float]

def calculate_classification_results(
    prediction: pd.Series, 
    target: pd.Series,
    prediction_proba: Union[pd.DataFrame, pd.Series] = None
    ) -> ClassificationResult:

    prediction = prediction.map(str)
    target = target.map(str)

    logloss = None
    roc_auc = None
    
    accuracy = accuracy_score(target, prediction)
    classification_info = classification_report(target, prediction, output_dict=True)
    classification_info.pop('accuracy')
    confusion_matrix = calculate_confusion_matrix_by_classes(target, prediction)
    mattheus_corr_coefficient = matthews_corrcoef(target, prediction)
    if prediction_proba is not None:
        try:
            roc_auc = {}
            roc_auc['ovr'] = float(roc_auc_score(y_true=target, y_score=prediction_proba, multi_class='ovr'))
            roc_auc['ovo'] = float(roc_auc_score(y_true=target, y_score=prediction_proba, multi_class='ovo'))
            logloss = log_loss(y_true=target, y_pred=prediction_proba)
        except:
            pass
    return ClassificationResult(
        accuracy = accuracy,
        confusion_matrix = confusion_matrix,
        classification_info = classification_info,
        logloss = logloss,
        roc_auc = roc_auc,
        mattheus_corr_coefficient = float(mattheus_corr_coefficient)
    )