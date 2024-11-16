import pandas as pd

def compatibilizar_series(data, *series, fill_value=pd.NaT):
    fecha_min, fecha_max = data.index.min(), data.index.max()
    rango_fechas = pd.date_range(start=fecha_min, end=fecha_max, freq='MS')
    data = data.reindex(rango_fechas)
    series_alineadas = [
        serie.reindex(rango_fechas, fill_value=fill_value).fillna(0).infer_objects(copy=False) 
        for serie in series
    ]
    return data, *series_alineadas
