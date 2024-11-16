import pandas as pd

def load_data(filepath):
    """
    Carga los datos desde un archivo CSV.
    """
    return pd.read_csv(filepath, sep=";")

def preprocess_data(data):
    """
    Procesa los datos, crea la columna 'fecha' como índice y 
    ajusta la frecuencia temporal.
    """
    df = data[["Anno", "Mes Central Trimestre", "Tasa oficial", "Tasa ajustada"]]
    
    # Convertimos columnas de año y mes en fecha
    df['fecha'] = pd.to_datetime(df.rename(columns={'Anno': 'year', 'Mes Central Trimestre': 'month'})
                                  .assign(day=1)[['year', 'month', 'day']])
    
    # Usamos la columna de fechas como índice
    df.set_index('fecha', inplace=True)
    
    # Frecuencia temporal mensual
    df.index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='MS')
    
    # Eliminamos las columnas que no son necesarias
    df = df.drop(['Anno', 'Mes Central Trimestre'], axis=1)
    
    return df
