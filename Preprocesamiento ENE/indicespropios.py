import pandas as pd

# Unimos todas las ENE anualizadas disponibles en la página.

csv_files = [f'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/ano-{year}.csv' for year in range(2010, 2024)]
# Añadir los archivos ENE enero-febrero-marzo y abril-mayo-junio de 2024

csv_files.extend([
    'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/eneefm.csv', 
    'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/eneamj.csv'
])

# Usamos las variables: AÑO, MES, SEXO, TRAMO_EDAD, REGION, CINE, PROVEEDOR, ACTIV, B7A_1, EST_CONYUGAL, B1, TIPO, CATEGORIA_OCUPACION

columns = ['ano_trimestre', 'mes_central', 'sexo', 'cae_especifico', 'edad']

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
    df['fecha_encuesta'] = pd.to_datetime(df['ano_trimestre'].astype(str) + '-' + df['mes_central'].astype(str), format='%Y-%m')
    
    # Convertir a categorías, aunque sí dudo un poco de si es formato category o string.
    categorical_columns = ['sexo', 'cae_especifico', 'edad']
    for col in categorical_columns:
        df[col] = df[col].astype('category')
    
    data_frames.append(df)

combined_df = pd.concat(data_frames, ignore_index=True)

combined_df.to_csv('indicespropios.csv', index=False)

