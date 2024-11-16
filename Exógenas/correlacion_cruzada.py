import matplotlib.pyplot as plt

def cross_correlations(series1, series2, lags=12):
    return [series1.corr(series2.shift(lag)) for lag in range(lags)]

def graficar_correlaciones(lags, *correlaciones, etiquetas):
    plt.figure(figsize=(10, 6))
    for correlacion, etiqueta in zip(correlaciones, etiquetas):
        plt.plot(lags, correlacion, marker='o', label=etiqueta)
    plt.title('Correlaciones Cruzadas para Diferentes Lags')
    plt.xlabel('Lag')
    plt.ylabel('Correlación')
    plt.axhline(0, color='gray', linewidth=0.5)
    plt.legend()
    plt.show()

