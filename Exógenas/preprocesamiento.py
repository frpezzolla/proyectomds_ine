import pandas as pd

def cargar_datos(ruta, sep=";",encoding="utf-8"):
    return pd.read_csv(ruta, sep=sep,encoding=encoding)

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

def preprocesar_pib(pib):
    pib['Periodo'] = pd.to_datetime(pib['Periodo'], format='%d-%m-%Y')
    dic = {"Periodo": "date", "1.PIB a precios corrientes": "pib_corrientes","2.PIB volumen a precios del a�o anterior encadenado":"pib_inflacion","3.PIB volumen a precios del a�o anterior encadenado (desestacionalizado)":"pib_inflacion_desestacionalizado"}
    df = pib.copy().rename(columns=dic)
    df = df.replace(",", ".", regex=True)
    df = df[df['date'].dt.year>=2010]
    columns = df.columns.tolist()
    num = [col for col in columns if col != 'date']
    df[num] = df[num].astype(float)

    df_disj = df.copy()
    df_disj.set_index('date', inplace=True)
    df.set_index('date', inplace=True)

    monthly_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq='MS')
    df = df.reindex(monthly_index)
    df = df.ffill()

    return df,df_disj

def preprocesar_ipc(ipc1,ipc2):
    ipc1['Periodo'] = pd.to_datetime(ipc1['Periodo'], format='%d-%m-%Y')
    ipc2['Periodo'] = pd.to_datetime(ipc2['Periodo'], format='%d-%m-%Y')
    data = pd.merge(ipc1, ipc2, on='Periodo', how='inner')
    columns = data.columns.tolist()
    dic = {"Periodo": "date",columns[1]:"IPC",columns[2]:"IPC_Sin_Volatiles"}
    df = data.copy().rename(columns=dic)
    df = df.replace(",", ".", regex=True)
    df = df[df['date'].dt.year>=2010]
    columns = df.columns.tolist()
    num = [col for col in columns if col != 'date']
    df[num] = df[num].astype(float)
    df.set_index('date', inplace=True)
    return df
