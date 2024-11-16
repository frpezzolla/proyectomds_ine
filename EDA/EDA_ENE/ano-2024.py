import pandas as pd

# Unimos todas las ENE anualizadas disponibles en la página.

csv_files = [f'ano-{year}.csv' for year in range(2010, 2024)]
# Añadir los archivos ENE enero-febrero-marzo y abril-mayo-junio de 2024

csv_files.extend(['eneefm.csv', 'eneamj.csv'])

# Usamos las variables: AÑO, MES, SEXO, TRAMO_EDAD, REGION, CINE, PROVEEDOR, ACTIV, B7A_1, EST_CONYUGAL, B1, TIPO, CATEGORIA_OCUPACION

columns = ['ano_encuesta', 'mes_encuesta', 'sexo', 'tramo_edad', 'region', 'cine', 'proveedor',
           'activ', 'b7a_1', 'est_conyugal', 'b1', 'tipo', 'categoria_ocupacion']

data_frames = []

# Leemos cada csv en la lista, y porsiacaso utilizamos encodings diferentes, evaluar si son necesarios, el sep=';' es propio de las ENE trimestrales
for file in csv_files:
    try:
        df = pd.read_csv(file, usecols=columns, encoding='latin1', sep=';')
    except UnicodeDecodeError:
        df = pd.read_csv(file, usecols=columns, encoding='ISO-8859-1', sep=';')
    except ValueError as e:
        print(f"Error processing {file}: {e}")
        continue
    
    # Convertir a datetime, escencial para las visualizaciones
    df['fecha_encuesta'] = pd.to_datetime(df['ano_encuesta'].astype(str) + '-' + df['mes_encuesta'].astype(str), format='%Y-%m')
    
    # Convertir a categorías, aunque sí dudo un poco de si es formato category o string.
    categorical_columns = ['sexo', 'tramo_edad', 'region', 'cine', 'proveedor', 'activ', 'b7a_1', 'est_conyugal', 'b1', 'tipo', 'categoria_ocupacion']
    for col in categorical_columns:
        df[col] = df[col].astype('category')
    
    data_frames.append(df)

combined_df = pd.concat(data_frames, ignore_index=True)

combined_df.to_csv('combined_data_2024.csv', index=False)

