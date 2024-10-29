from statsmodels.tsa.stattools import coint, grangercausalitytests
import pandas as pd

def prueba_cointegracion(serie1, serie2):
    coint_resultado = coint(serie1, serie2)
    return {'Estadístico': coint_resultado[0], 'p-valor': coint_resultado[1]}

def prueba_granger(data, serie, maxlag=12):
    df_granger = pd.concat([data, serie], axis=1)
    return grangercausalitytests(df_granger.dropna(), maxlag=maxlag, verbose=False)
