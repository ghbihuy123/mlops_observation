from ...calculator.classification_performance import calculate_confusion_by_classes 
from sklearn.metrics import confusion_matrix
def calculate_confusion_matrix_by_classes(y_true, y_pred):
    labels = list(set(y_true) | set(y_pred))
    confusion_matrix_inf = confusion_matrix(y_true, y_pred, labels=labels)
    return calculate_confusion_by_classes(confusion_matrix_inf, class_names=labels)