from sklearn.metrics import mean_absolute_error

def calculate_mae(y_true, y_pred):
    """
    Calcula el Error Absoluto Medio (MAE) entre los valores reales y los predichos.
    """
    return mean_absolute_error(y_true, y_pred)
