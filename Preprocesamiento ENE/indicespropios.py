import pandas as pd

# Unimos todas las ENE anualizadas disponibles en la página.

csv_files = [f'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/ano-{year}.csv' for year in range(2010, 2024)]
# Añadir los archivos ENE enero-febrero-marzo y abril-mayo-junio de 2024

csv_files.extend([
    'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/eneefm.csv', 
    'C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/Databases/eneamj.csv'
])


columns = ['ano_trimestre', 'mes_central', 'sexo', 'cae_especifico', 'edad']

data_frames = []

# Leemos todos los csv en la lista de una vez, utilizando el sep=';' propio de las ENE trimestrales
df = pd.concat(
    [pd.read_csv(file, usecols=columns, encoding='latin1', sep=';') for file in csv_files],
    ignore_index=True
)

# Convertir a datetime, escencial para las visualizaciones
df['fecha_encuesta'] = pd.to_datetime(df['ano_trimestre'].astype(str) + '-' + df['mes_central'].astype(str), format='%Y-%m')

# Convertir a categorías, aunque sí dudo un poco de si es formato category o string.
categorical_columns = ['sexo', 'cae_especifico', 'edad']
for col in categorical_columns:
    df[col] = df[col].astype('category')

df.to_csv('indicespropios.csv', index=False)

