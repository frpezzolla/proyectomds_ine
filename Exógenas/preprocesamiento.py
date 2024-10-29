import pandas as pd

def cargar_datos(ruta, sep=";"):
    return pd.read_csv(ruta, sep=sep)

def preprocesar_tasa_trimestral(data):
    data = data.copy()
    data[['Tasa oficial', 'Tasa ajustada']] = data[['Tasa oficial', 'Tasa ajustada']].astype(float)
    data['Fecha'] = pd.to_datetime(data['Anno'].astype(str) + '-' + data['Mes Central Trimestre'].astype(str))
    data.drop(columns=['Trimestre'], inplace=True)
    data.set_index('Fecha', inplace=True)
    return data[['Tasa oficial', 'Tasa ajustada']]

def preprocesar_imacec(imacec):
    imacec = imacec.copy()
    imacec['1.Imacec'] = imacec['1.Imacec'].str.replace(',', '.').astype(float)
    imacec['Periodo'] = pd.to_datetime(imacec['Periodo'], format='%d-%m-%Y')
    imacec['Año_Mes'] = imacec['Periodo'].dt.to_period('M')
    imacec['Fecha'] = imacec['Año_Mes'].dt.to_timestamp()
    imacec.set_index('Fecha', inplace=True)
    imacec.drop(columns=['Año_Mes','Periodo'], inplace=True)
    return imacec.rename(columns={'1.Imacec': 'imacec'})

def preprocesar_defunciones(defunciones):
    defunciones = defunciones.copy()
    defunciones['FECHA_DEF'] = pd.to_datetime(defunciones['FECHA_DEF'])
    defunciones['Año_Mes'] = defunciones['FECHA_DEF'].dt.to_period('M')
    defunciones_mensuales = defunciones.groupby('Año_Mes').size().reset_index(name='Total_Defunciones')
    defunciones_mensuales['Fecha'] = defunciones_mensuales['Año_Mes'].dt.to_timestamp()
    return defunciones_mensuales.set_index('Fecha').drop(columns='Año_Mes')

def preprocesar_casos_confirmados(casos_confirmados):
    casos_chile = casos_confirmados.copy()
    casos_chile = casos_chile[casos_chile['Entity'] == 'Chile']
    casos_chile.drop(columns=['Entity', 'Code'], inplace=True)
    casos_chile['Day'] = pd.to_datetime(casos_chile['Day'])
    casos_chile['Year_Month'] = casos_chile['Day'].dt.to_period('M')
    casos_mensuales = casos_chile.groupby('Year_Month')['Daily new confirmed cases of COVID-19 per million people (rolling 7-day average, right-aligned)'].sum().reset_index()
    casos_mensuales = casos_mensuales.rename(columns={'Daily new confirmed cases of COVID-19 per million people (rolling 7-day average, right-aligned)': 'total casos'})
    casos_mensuales['Fecha'] = casos_mensuales['Year_Month'].dt.to_timestamp()
    return casos_mensuales.set_index('Fecha').drop(columns='Year_Month')

