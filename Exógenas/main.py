from preprocesamiento import (
    cargar_datos,
    preprocesar_tasa_trimestral,
    preprocesar_imacec,
    preprocesar_defunciones,
    preprocesar_casos_confirmados
)
from compatibilizacion import compatibilizar_series
from correlacion_cruzada import cross_correlations, graficar_correlaciones
from visualizacion import graficar_series_estandarizadas
from analisis_estadistico import prueba_cointegracion, prueba_granger
from utilidades import exportar_csv

# Cargar y preprocesar datos
data = preprocesar_tasa_trimestral(cargar_datos("./Datos/tasa_trimestral.csv"))
imacec = preprocesar_imacec(cargar_datos("./Datos/imacec.csv"))
defunciones = preprocesar_defunciones(cargar_datos("./Datos/defunciones.csv"))
casos = preprocesar_casos_confirmados(cargar_datos("./Datos/casos_confirmados.csv",sep=","))

# Compatibilizar series
data, imacec, defunciones, casos = compatibilizar_series(data, imacec, defunciones, casos)

# Exportamos opcionalmente
exportar_csv(data, filename="desocupacion.csv",directory="./Datos/processed")
exportar_csv(imacec, filename="imacec.csv",directory="./Datos/processed")
exportar_csv(defunciones, filename="defunciones.csv",directory="./Datos/processed")
exportar_csv(casos, filename="casos.csv",directory="./Datos/processed")

# Cálculo de correlaciones cruzadas
cross_corr_imacec = cross_correlations(data['Tasa oficial'], imacec['imacec'])
cross_corr_defunciones = cross_correlations(data['Tasa oficial'], defunciones['Total_Defunciones'])
cross_corr_casos = cross_correlations(data['Tasa oficial'], casos['total casos'])

# Graficar correlaciones cruzadas
#graficar_correlaciones(
#    list(range(len(cross_corr_imacec))),
#    cross_corr_imacec, cross_corr_defunciones, cross_corr_casos,
#    etiquetas=['IMACEC', 'Defunciones', 'Casos Confirmados']
#)

# Graficar series estandarizadas
#graficar_series_estandarizadas(data, imacec, defunciones, casos)



