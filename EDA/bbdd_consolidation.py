# Unificacion de bases de datos

# Paquetes-------------------------------------
import pandas as pd
import numpy as np

#Limpieza manual de errores -----------------------------------------------------------------------------------
# 
#file_path = "./Datos/ano-2023.csv"

# Abre el archivo en modo de lectura binaria para evitar problemas de codificación
#with open(file_path, 'rb') as file:
#    line_number = 0
#    for line in file:
#        try:
            # Intenta decodificar cada línea en utf-8
#            line.decode('utf-8')
#        except UnicodeDecodeError as e:
#            print(f"Error en la línea {line_number}: {e}")
#            break  # O seguir revisando para encontrar más errores
#        line_number += 1

# Datos----------------------------------------
# Datos disponibles en https://www.ine.gob.cl/estadisticas/sociales/mercado-laboral/ocupacion-y-desocupacion
# Se utilizan las bases de datos anualizadas y la de los dos primeros trimestres del 2024
bd2010 = pd.read_csv("./Datos/ano-2010.csv",sep=";") # Tipos mezclados en columna 28
bd2011 = pd.read_csv("./Datos/ano-2011.csv",sep=";") # Tipos mezclados en columna 28
bd2012 = pd.read_csv("./Datos/ano-2012.csv",sep=";")
bd2013 = pd.read_csv("./Datos/ano-2013.csv",sep=";")
bd2014 = pd.read_csv("./Datos/ano-2014.csv",sep=";")
bd2015 = pd.read_csv("./Datos/ano-2015.csv",sep=";")
bd2016 = pd.read_csv("./Datos/ano-2016.csv",sep=";")
bd2017 = pd.read_csv("./Datos/ano-2017.csv",sep=";")
bd2018 = pd.read_csv("./Datos/ano-2018.csv",sep=";")
bd2019 = pd.read_csv("./Datos/ano-2019.csv",sep=";")
bd2020 = pd.read_csv("./Datos/ano-2020.csv",sep=";")
bd2021 = pd.read_csv("./Datos/ano-2021.csv",sep=";")
bd2022 = pd.read_csv("./Datos/ano-2022.csv",sep=";")
bd2023 = pd.read_csv("./Datos/ano-2023.csv",sep=";")
bd2024_2 = pd.read_csv("./Datos/ene-2024-02-efm.csv",sep=";")
bd2024_5 = pd.read_csv("./Datos/ene-2024-05-amj.csv",sep=";")


# Columnas con distintos tipos
# Analizamos las variables que tienen distintos tipos
# Columnas {1:[28],2:[28],3:[28],4:[28],5:[28,60],6:[28],7:[28],8:[28],9:[28],10:[28,126],11:[27,41,88,113,146,151],12:[27,41,78,92],13:[27,41,88,113,151],14:[27,41,75,87,112,150,157]}

#columns_2010 = bd2010.columns.tolist()
#columns_2011 = bd2011.columns.tolist()
#columns_2012 = bd2012.columns.tolist()
#columns_2013 = bd2013.columns.tolist()
#columns_2014 = bd2014.columns.tolist()
#columns_2015 = bd2015.columns.tolist()
#columns_2016 = bd2016.columns.tolist()
#columns_2017 = bd2017.columns.tolist()
#columns_2018 = bd2018.columns.tolist()
#columns_2019 = bd2019.columns.tolist()
#columns_2020 = bd2020.columns.tolist()
#columns_2021 = bd2021.columns.tolist()
#columns_2022 = bd2022.columns.tolist()
#columns_2023 = bd2023.columns.tolist()

#columns_list = [columns_2010,columns_2011,columns_2012,columns_2013,columns_2014,columns_2015,columns_2016,columns_2017,columns_2018,columns_2019,columns_2020,columns_2021,columns_2022,columns_2023]

# Vemos si las columnas son iguales entre años respecto al 2010
#for i in range(len(columns_list)-1):
    #print(columns_2010 == columns_list[i+1])
# Respecto al 2020 cuando se reralizó el cambio de códigos
#for i in range(10,len(columns_list)):
    #print(columns_2020 == columns_list[i])
# Casi ningún año tiene las mismas columnas entre sí.

# Columnas con errores
#indexes = [28,60,126,41,88,113,146,151,78,92,27,87,112,150,157]

# Creación de la columna de actividad anual
# Extraemos solamente la columna de interés activ
activ2010 = bd2010.loc[:,["ano_trimestre","mes_central","activ"]]
activ2011 = bd2011.loc[:,["ano_trimestre","mes_central","activ"]]
activ2012 = bd2012.loc[:,["ano_trimestre","mes_central","activ"]]
activ2013 = bd2013.loc[:,["ano_trimestre","mes_central","activ"]]
activ2014 = bd2014.loc[:,["ano_trimestre","mes_central","activ"]]
activ2015 = bd2015.loc[:,["ano_trimestre","mes_central","activ"]]
activ2016 = bd2016.loc[:,["ano_trimestre","mes_central","activ"]]
activ2017 = bd2017.loc[:,["ano_trimestre","mes_central","activ"]]
activ2018 = bd2018.loc[:,["ano_trimestre","mes_central","activ"]]
activ2019 = bd2019.loc[:,["ano_trimestre","mes_central","activ"]]
activ2020 = bd2020.loc[:,["ano_trimestre","mes_central","activ"]]
activ2021 = bd2021.loc[:,["ano_trimestre","mes_central","activ"]]
activ2022 = bd2022.loc[:,["ano_trimestre","mes_central","activ"]]
activ2023 = bd2023.loc[:,["ano_trimestre","mes_central","activ"]]
activ2024_2 = bd2024_2.loc[:,["ano_trimestre","mes_central","activ"]]
activ2024_5 = bd2024_5.loc[:,["ano_trimestre","mes_central","activ"]]

# 1 es ocupado
# 2 es desocupado
# 3 es fuera de la fuerza de trabajo

# Concatenamos
df_ocup = pd.concat([activ2010,activ2011,activ2012,activ2013,activ2014,activ2015,activ2016,activ2017,activ2018,activ2019,activ2020,activ2021,activ2022,activ2023,activ2024_2,activ2024_5], ignore_index=True)
df_ocup = df_ocup.sort_values(by=['ano_trimestre','mes_central']).reset_index(drop=True)
#print(df_ocup.shape)
#(5939008, 3)
#print(df_ocup.head())


# Especifica el directorio y el nombre del archivo
directorio = './Datos/'
nombre_archivo = 'base2010-2024_5.csv'

# Exportar el DataFrame como CSV
df_ocup.to_csv(f'{directorio}{nombre_archivo}', index=False)

