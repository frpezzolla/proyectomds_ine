import pandas as pd

# 1. Lectura del archivo CSV generado
df = pd.read_csv('C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Preprocesamiento ENE/indicespropios.csv')

# 2. Filtrar y agrupar por trimestre (ano_trimestre) y mes_central
# Desocupados (cae_especifico 8-9) por edad y sexo
dh15 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'].between(15, 24)) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='dh15')
dm15 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'].between(15, 24)) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='dm15')
dh25 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'] >= 25) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='dh25')
dm25 = df[(df['cae_especifico'].isin([8, 9])) & (df['edad'] >= 25) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='dm25')

# Ocupados (cae_especifico 1-7) por edad y sexo
oh15 = df[(df['cae_especifico'].isin([1, 7])) & (df['edad'].between(15, 24)) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='oh15')
om15 = df[(df['cae_especifico'].isin([1, 7])) & (df['edad'].between(15, 24)) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='om15')
oh25 = df[(df['cae_especifico'].isin([1, 7])) & (df['edad'] >= 25) & (df['sexo'] == 1)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='oh25')
om25 = df[(df['cae_especifico'].isin([1, 7])) & (df['edad'] >= 25) & (df['sexo'] == 2)].groupby(['ano_trimestre', 'mes_central'])['ano_trimestre'].count().reset_index(name='om25')

# 3. Combinamos los dataframes por 'ano_trimestre' y 'mes_central'
m1 = pd.concat([dh15, dm15['dm15'], dh25['dh25'], dm25['dm25'], 
                oh15['oh15'], om15['om15'], oh25['oh25'], om25['om25']], axis=1)

# 4. Calcular totales de desocupados y ocupados
m1['desocupados'] = m1[['dh15', 'dm15', 'dh25', 'dm25']].sum(axis=1)
m1['ocupados'] = m1[['oh15', 'om15', 'oh25', 'om25']].sum(axis=1)

# Calcular los desocupados y ocupados por sexo
m1['dh'] = m1[['dh15', 'dh25']].sum(axis=1)
m1['dm'] = m1[['dm15', 'dm25']].sum(axis=1)
m1['oh'] = m1[['oh15', 'oh25']].sum(axis=1)
m1['om'] = m1[['om15', 'om25']].sum(axis=1)

# 5. Fuerza de trabajo por sexo y total
m1['ft_h'] = m1[['dh', 'oh']].sum(axis=1)
m1['ft_m'] = m1[['dm', 'om']].sum(axis=1)
m1['ft'] = m1[['desocupados', 'ocupados']].sum(axis=1)

# 6. Calcular las tasas de desocupación para cada trimestre y mes central
m1['td_h'] = (m1['dh'] / m1['ft_h']) * 100  # Tasa desocupados hombres
m1['td_m'] = (m1['dm'] / m1['ft_m']) * 100  # Tasa desocupados mujeres
m1['td'] = (m1['desocupados'] / m1['ft']) * 100  # Tasa desocupación total

# 7. Revisar los resultados
print(m1.head())

# Exportar a CSV en formato con tasas por trimestre y mes central
m1.to_csv('C:/Users/Rodrigo/Desktop/MDS_INE/proyectomds_ine/Prophet/tasaspropias.csv', index=False)
