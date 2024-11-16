import os

def exportar_csv(dataframe, filename="serie_procesada.csv", directory="exported_data"):
    """
    Exporta un dataframe a un archivo CSV en el directorio especificado.
    
    Parámetros:
    - dataframe: DataFrame a exportar.
    - filename: Nombre del archivo (por defecto 'serie_procesada.csv').
    - directory: Directorio donde se guardará el archivo (por defecto 'exported_data').
    """
    # Crear el directorio si no existe
    os.makedirs(directory, exist_ok=True)
    
    # Ruta completa del archivo
    filepath = os.path.join(directory, filename)
    
    # Exportar el dataframe a CSV
    dataframe.to_csv(filepath, index=True)
    print(f"Archivo exportado con éxito en: {filepath}")
