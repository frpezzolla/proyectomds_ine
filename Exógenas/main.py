from preprocesamiento import (
    cargar_datos,
    preprocesar_tasa_trimestral,
    preprocesar_imacec,
    preprocesar_defunciones,
    preprocesar_casos_confirmados,
    preprocesar_pib,
    preprocesar_ipc
)
from compatibilizacion import compatibilizar_series
from correlacion_cruzada import cross_correlations, graficar_correlaciones
from visualizacion import graficar_series_estandarizadas,plot_series,estandarizar
from analisis_estadistico import prueba_cointegracion, prueba_granger
from utilidades import exportar_csv
import pandas as pd

# Cargar y preprocesar datos
data = preprocesar_tasa_trimestral(cargar_datos("./Datos/tasa_trimestral.csv"))
imacec = preprocesar_imacec(cargar_datos("./Datos/imacec.csv"))
defunciones = preprocesar_defunciones(cargar_datos("./Datos/defunciones.csv"))
casos = preprocesar_casos_confirmados(cargar_datos("./Datos/casos_confirmados.csv",sep=","))
pib,pib_disj = preprocesar_pib(cargar_datos("./Datos/PIBs.csv",sep=";"))
ipc = preprocesar_ipc(cargar_datos("./Datos/IPC_empalmado.csv",sep=";",encoding="ISO-8859-1"),cargar_datos("./Datos/IPC_no_volatiles_empalmado.csv",sep=";",encoding="ISO-8859-1"))

# Compatibilizar series
data, imacec, defunciones, casos, pib, ipc = compatibilizar_series(data, imacec, defunciones, casos, pib, ipc)

# Todo a un dataframe
df = pd.concat([data, imacec, defunciones, casos, pib, ipc],axis=1,join='inner')

# Estandarizamos
df_std=estandarizar(df)

columns = df.columns.tolist()

#print(df_std)

# Cálculo de correlaciones cruzadas
cross_corr_imacec = cross_correlations(df_std['Tasa oficial'], df_std['imacec'])
cross_corr_defunciones = cross_correlations(df_std['Tasa oficial'], df_std['Total_Defunciones'])
cross_corr_casos = cross_correlations(df_std['Tasa oficial'], df_std['total casos'])
cross_corr_pib = cross_correlations(df_std['Tasa oficial'], df_std['pib_inflacion_desestacionalizado'])
cross_corr_ipc = cross_correlations(df_std['Tasa oficial'], df_std['IPC_Sin_Volatiles'])

cross_corr_pib_stationality = cross_correlations(df_std['Tasa ajustada'], df_std['pib_inflacion_desestacionalizado'])

# Graficar correlaciones cruzadas
graficar_correlaciones(
    list(range(len(cross_corr_imacec))),
    cross_corr_imacec, cross_corr_defunciones, cross_corr_casos,cross_corr_pib_stationality,cross_corr_ipc,
    etiquetas=['IMACEC', 'Defunciones', 'Casos Confirmados','PIB vs Tasa Ajustada','IPC']
)

# Se encuentra que la variable que más explica la tasa de desocupación es el IPC, y el PIB
# junto con el IMACEC explican una porción similar de la tasa. Las 3 correlaciones se tienden
# a estabiliza después de 6 u 8 meses de lags manteniendose aproximadamente constantes.

# Matriz de correlaciones entre variables
correlation_matrix = df_std[['imacec','Total_Defunciones','total casos','pib_inflacion_desestacionalizado','IPC_Sin_Volatiles']].corr(method='spearman')
#print(correlation_matrix)

# Encontramos que las correlaciones entre variables macroeconómicas en demasiado alta para 
# incluir dos en un modelo al mismo tiempo, de forma de evitar problemas de endogeneidad.
# Por esto, se decidió incluir 3 modelos con cada variables macroeconómica mas el indicador
# covid que menos correlación tiene con cada indicador, que es Total_Defunciones
# Así, cada modelo incluirá los sets de variables ["imacec","Total_Defunciones"],
# ["pib_inflacion_desestacionalizado","Total_Defunciones"],["IPC_Sin_Volatiles","Total_Defunciones"]. 

# Exportamos opcionalmente
exportar_csv(df, filename="tasas+exo.csv",directory="./Datos/processed")


