import pandas as pd

# 1. Lectura del archivo CSV
df = pd.read_csv('C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/indicespropios.csv')

# 2. Contar desocupados por sexo y grupo de edad (con fact_cal o sin ella si no existe)
if 'fact_cal' not in df.columns:
    df['fact_cal'] = 1  # Usar conteo simple si 'fact_cal' no está disponible

# 3. Agrupar por año y trimestre (ano_trimestre) para cada grupo de interés
dh15 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'].between(15, 24)) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='dh15')
dm15 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'].between(15, 24)) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='dm15')
dh25 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'] >= 25) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='dh25')
dm25 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'] >= 25) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='dm25')

# Ocupados (cae_especifico 1-7) por edad y sexo
oh15 = df[(df['cae_especifico'].isin([1, 2, 3, 4, 5, 6, 7])) & (df['edad'].between(15, 24)) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='oh15')
om15 = df[(df['cae_especifico'].isin([1, 2, 3, 4, 5, 6, 7])) & (df['edad'].between(15, 24)) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='om15')
oh25 = df[(df['cae_especifico'].isin([1, 2, 3, 4, 5, 6, 7])) & (df['edad'] >= 25) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='oh25')
om25 = df[(df['cae_especifico'].isin([1, 2, 3, 4, 5, 6, 7])) & (df['edad'] >= 25) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['fact_cal'].sum().reset_index(name='om25')

# 4. Combinar los resultados en un único DataFrame
m1 = pd.concat([dh15, dm15['dm15'], dh25['dh25'], dm25['dm25'], 
                oh15['oh15'], om15['om15'], oh25['oh25'], om25['om25']], axis=1)

# 5. Calcular totales de desocupados y ocupados
m1['desocupados'] = m1[['dh15', 'dm15', 'dh25', 'dm25']].sum(axis=1)
m1['ocupados'] = m1[['oh15', 'om15', 'oh25', 'om25']].sum(axis=1)

# Calcular los desocupados y ocupados por sexo
m1['dh'] = m1[['dh15', 'dh25']].sum(axis=1)
m1['dm'] = m1[['dm15', 'dm25']].sum(axis=1)
m1['oh'] = m1[['oh15', 'oh25']].sum(axis=1)
m1['om'] = m1[['om15', 'om25']].sum(axis=1)

# 6. Calcular la fuerza de trabajo por sexo y total
m1['ft_h'] = m1[['dh', 'oh']].sum(axis=1)
m1['ft_m'] = m1[['dm', 'om']].sum(axis=1)
m1['ft'] = m1[['desocupados', 'ocupados']].sum(axis=1)

# 7. Calcular las tasas de desocupación por cada trimestre y mes central
m1['td_h'] = (m1['dh'] / m1['ft_h']) * 100  # Tasa de desocupados hombres
m1['td_m'] = (m1['dm'] / m1['ft_m']) * 100  # Tasa de desocupados mujeres
m1['td'] = (m1['desocupados'] / m1['ft']) * 100  # Tasa de desocupación total

# 8. Añadir las columnas de año y trimestre
m1['ano'] = df['ano_trimestre']
m1['mes'] = df['mes_central']

# 9. Mostrar el resultado
print(m1.head())

# Exportar a CSV el resultado ajustado por trimestre y mes central
m1.to_csv('C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Prophet/tasaspropias.csv', index=False)
