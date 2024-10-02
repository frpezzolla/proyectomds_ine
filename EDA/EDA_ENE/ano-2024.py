import pandas as pd

# Lista de archivos CSV desde 2010 hasta 2023
csv_files = [f'C:/Users/rodri/OneDrive/Escritorio/MDS/Proyecto de Ciencia de Datos/proyectomds_ine/data/ano-{year}.csv' for year in range(2010, 2024)]
# Añadir los archivos de 2024
csv_files.extend(['eneefm.csv', 'eneamj.csv'])

# Columnas deseadas
columns = ['ano_encuesta', 'mes_encuesta', 'sexo', 'tramo_edad', 'region', 'cine', 'proveedor',
           'activ', 'b7a_1', 'est_conyugal', 'b1', 'tipo', 'categoria_ocupacion']

# Lista para almacenar los DataFrames
data_frames = []

# Leer y procesar cada archivo CSV
for file in csv_files:
    try:
        df = pd.read_csv(file, usecols=columns, encoding='latin1', sep=';')
    except UnicodeDecodeError:
        df = pd.read_csv(file, usecols=columns, encoding='ISO-8859-1', sep=';')
    except ValueError as e:
        print(f"Error processing {file}: {e}")
        continue
    
    # Convertir ano_encuesta y mes_encuesta a formato datetime
    df['fecha_encuesta'] = pd.to_datetime(df['ano_encuesta'].astype(str) + '-' + df['mes_encuesta'].astype(str), format='%Y-%m')
    
    # Convertir las variables categóricas a tipo 'category'
    categorical_columns = ['sexo', 'tramo_edad', 'region', 'cine', 'proveedor', 'activ', 'b7a_1', 'est_conyugal', 'b1', 'tipo', 'categoria_ocupacion']
    for col in categorical_columns:
        df[col] = df[col].astype('category')
    
    data_frames.append(df)

# Concatenar todos los DataFrames
combined_df = pd.concat(data_frames, ignore_index=True)

# Guardar el DataFrame combinado en un nuevo archivo CSV
combined_df.to_csv('combined_data_2024.csv', index=False)

