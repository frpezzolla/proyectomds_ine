from data_processing import load_data, preprocess_data
from stl_decomposition import decompose_stl
from metrics import calculate_mae
from visualization import plot_series_comparison, plot_error

def main():
    # Cargar y procesar datos
    data = load_data("./Datos/tasa_trimestral.csv")
    df = preprocess_data(data)
    
    # Descomponer con STL
    result, df = decompose_stl(df)
    
    # Graficar comparación de la serie ajustada con la serie real
    plot_series_comparison(df, "Comparación de Tasa Oficial vs Serie Ajustada (STL)", "Tasa oficial", "Serie ajustada")
    
    # Calcular el MAE entre la serie real y ajustada
    mae_total = calculate_mae(df['Tasa oficial'], df['Serie ajustada'])
    print(f"El Error Absoluto Medio (MAE) del ajuste STL es: {mae_total}")
    
    # Graficar el error (y_real - y_ajustado)
    df['Error'] = df['Tasa oficial'] - df['Serie ajustada']
    plot_error(df, 'Error', "Error entre la Tasa Oficial y la Serie Ajustada (STL)")
    
    # Comparar tasas desestacionalizadas
    plot_series_comparison(df, "Comparación de Tasa Ajustada (INE) vs Serie Desestacionalizada (STL)", "Tasa ajustada", "Serie desestacionalizada")
    
    # Calcular el MAE entre tasas desestacionalizadas
    mae_desestacionalizada = calculate_mae(df['Tasa ajustada'], df['Serie desestacionalizada'])
    print(f"El Error Absoluto Medio (MAE) entre la serie desestacionalizada por STL y la tasa ajustada oficial es: {mae_desestacionalizada}")
    
    # Filtrar datos entre 2010 y septiembre de 2019
    df_filtered = df.loc['2010-01-01':'2019-09-30']
    mae_filtered = calculate_mae(df_filtered['Tasa ajustada'], df_filtered['Serie desestacionalizada'])
    print(f"El Error Absoluto Medio (MAE) entre 2010 y septiembre de 2019 es: {mae_filtered}")

if __name__ == "__main__":
    main()
