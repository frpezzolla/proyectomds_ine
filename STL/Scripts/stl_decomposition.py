from statsmodels.tsa.seasonal import STL

def decompose_stl(data, seasonal=13, robust=True):
    """
    Aplica la descomposición STL a la serie de tiempo.
    """
    stl = STL(data['Tasa oficial'], seasonal=seasonal, robust=robust)
    result = stl.fit()
    
    # Agregamos las componentes de tendencia y estacionalidad al DataFrame
    data['Serie ajustada'] = result.trend + result.seasonal
    data['Serie desestacionalizada'] = data['Tasa oficial'] - result.seasonal
    return result, data
