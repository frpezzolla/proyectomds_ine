import matplotlib.pyplot as plt
import pandas as pd

def estandarizar(serie):
    return (serie - serie.mean()) / serie.std()

def graficar_series_estandarizadas(data, imacec, defunciones, casos):
    plt.figure(figsize=(12, 8))
    plt.plot(data.index, estandarizar(data['Tasa oficial']), label='Tasa Oficial', color='blue')
    plt.plot(imacec.index, estandarizar(imacec['imacec']), label='IMACEC', color='green')
    plt.plot(imacec.index, estandarizar(imacec['imacec'].shift(-6)), linestyle='--', label='IMACEC (lag 6 meses)', color='green')
    plt.plot(defunciones.index, estandarizar(defunciones['Total_Defunciones']), label='Defunciones', color='red')
    plt.plot(casos.index, estandarizar(casos['total casos']), label='Casos Confirmados', color='purple')
    plt.axvline(pd.Timestamp('2022-05-31'), color='green', linestyle='--', label='Final Mayo 2022')
    plt.axvline(pd.Timestamp('2023-05-31'), color='orange', linestyle='--', label='Final Mayo 2023')
    plt.title('Series de Tiempo Estandarizadas')
    plt.xlabel('Fecha')
    plt.ylabel('Valores Estandarizados')
    plt.legend()
    plt.show()

