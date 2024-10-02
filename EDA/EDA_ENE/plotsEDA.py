import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Etiquetas de las variables
sexo_labels = {1: 'Hombre', 2: 'Mujer'}
tramo_edad_labels = {
    1: '15 a 19 años', 2: '20 a 24 años', 3: '25 a 29 años', 4: '30 a 34 años',
    5: '35 a 39 años', 6: '40 a 44 años', 7: '45 a 49 años', 8: '50 a 54 años',
    9: '55 a 59 años', 10: '60 a 64 años', 11: '65 a 69 años', 12: '70 años o más'
}
region_labels = {
    1: 'Tarapacá', 2: 'Antofagasta', 3: 'Atacama', 4: 'Coquimbo', 5: 'Valparaíso', 
    6: 'O\'Higgins', 7: 'Maule', 8: 'Biobío', 9: 'La Araucanía', 10: 'Los Lagos',
    11: 'Aysén', 12: 'Magallanes', 13: 'Metropolitana', 14: 'Los Ríos', 15: 'Arica y Parinacota', 16: 'Ñuble'
}
cine_labels = {
    1: 'Nunca estudió', 2: 'Educación preescolar', 3: 'Educación primaria (nivel 1)', 
    4: 'Educación primaria (nivel 2)', 5: 'Educación secundaria',
    6: 'Educación Técnica (no Universitaria)', 7: 'Educación universitaria',
    8: 'Post títulos y maestría', 9: 'Doctorado', 99: 'No sabe'
}
proveedor_labels = {0: 'No corresponde', 1: 'Proveedor principal'}
cotizacion_labels = {1: 'Sí', 2: 'No'}
estado_civil_labels = {
    0: 'No aplica', 1: 'Casado/a', 2: 'Conviviente', 3: 'Soltero/a', 
    4: 'Viudo/a', 5: 'Separado/a de hecho', 6: 'Divorciado/a', 88: 'No sabe', 99: 'No responde'
}
tipo_labels = {
    1: 'Ciudad (CD)', 2: 'Resto de Área Urbana (RAU)', 3: 'Rural'
}
categoria_ocupacion_labels = {
    0: 'No corresponde', 1: 'Empleador', 2: 'Cuenta propia', 3: 'Asalariado sector privado', 
    4: 'Asalariado sector público', 5: 'Personal de servicio doméstico puertas afuera', 
    6: 'Personal de servicio doméstico puertas adentro', 7: 'Familiar o personal no remunerado'
}

# Leer el DataFrame desde el archivo CSV
df = pd.read_csv('combined_data_2024.csv', parse_dates=['fecha_encuesta'])

# Filtrar los datos donde 'activ' es igual a 2 (desocupados)
df_filtered = df[df['activ'] == 1].copy()

# Eliminar valores no informativos
df_filtered = df_filtered[~df_filtered['est_conyugal'].isin([77, 88, 99])]  # Eliminar No aplica, No sabe, No responde
df_filtered = df_filtered[~df_filtered['b7a_1'].isin([77, 88, 99])]  # Eliminar No aplica, No sabe, No responde
df_filtered = df_filtered[~df_filtered['cine'].isin([77, 88, 99])]  # Eliminar No aplica, No sabe, No responde
df_filtered = df_filtered[df_filtered['proveedor'] != 0]  # Eliminar No corresponde

# Eliminar filas con valores NaN en las columnas relevantes
df_filtered = df_filtered.dropna(subset=['proveedor', 'cine'])

# Agregar columna 'year_month' que contiene año y mes correctamente convertida
df_filtered['year_month'] = df_filtered['fecha_encuesta'].dt.to_period('M').dt.to_timestamp()

# Función para crear gráficos individuales para cada valor de una variable
def crear_grafico_por_valor(df, x_var, y_var, filtro_var, valor_filtro, etiquetas, title, labels, file_name):
    try:
        # Filtrar los datos por el valor específico de la variable
        df_filtro = df[df[filtro_var] == valor_filtro]

        # Comprobar si el DataFrame filtrado está vacío
        if df_filtro.empty:
            print(f"Sin datos para el valor {valor_filtro} de la variable {filtro_var}")
            return

        # Contar la frecuencia por mes
        frequency_by_month = df_filtro.groupby(x_var).size().reset_index(name='frequency')

        # Comprobar si la frecuencia está vacía después del agrupamiento
        if frequency_by_month.empty:
            print(f"El filtro para {valor_filtro} resultó en un DataFrame vacío después del agrupamiento.")
            return

        # Separar los datos en antes y después de enero de 2020
        before_2020 = frequency_by_month[frequency_by_month[x_var] < '2020-01-01']
        after_2020 = frequency_by_month[frequency_by_month[x_var] >= '2020-01-01']

        # Crear la figura
        fig = go.Figure()

        # Agregar la línea antes de 2020 en color azul, con marcadores
        fig.add_trace(go.Scatter(x=before_2020[x_var], y=before_2020[y_var],
                                 mode='lines+markers',
                                 line=dict(color='blue'),
                                 marker=dict(size=6),
                                 showlegend=False))

        # Agregar la línea después de 2020 en color rojo, con marcadores
        fig.add_trace(go.Scatter(x=after_2020[x_var], y=after_2020[y_var],
                                 mode='lines+markers',
                                 line=dict(color='red'),
                                 marker=dict(size=6),
                                 showlegend=False))

        # Comprobar si el DataFrame tiene datos válidos para determinar el valor máximo del eje Y
        y_max = max(frequency_by_month[y_var]) if not frequency_by_month.empty else 0

        # Agregar una línea vertical para indicar el inicio de la pandemia (enero de 2020)
        fig.add_vline(x='2020-01-01', line_width=2, line_dash="dash", line_color="green")

        # Agregar una anotación indicando "Inicio de la pandemia"
        fig.add_annotation(x='2020-01-01', y=y_max,
                           text="Inicio de la pandemia",
                           showarrow=True, arrowhead=1, ax=-50, ay=-50, bgcolor="yellow")

        # Actualizar el diseño del gráfico
        fig.update_layout(
            title=title,
            yaxis_title=labels[y_var],
            xaxis_title=labels[x_var],
            font=dict(
                family="Arial, sans-serif",
                size=14,
                color="Black"
            ),
            showlegend=False,  # Desactivar la leyenda
            plot_bgcolor='rgba(240, 248, 255, 0.9)',  # Color de fondo
            margin=dict(l=40, r=40, t=40, b=40),  # Márgenes optimizados para PowerPoint
            width=927,  # Anchura en píxeles
            height=300  # Altura en píxeles
        )

        # Guardar el gráfico como PDF
        pio.write_image(fig, file_name)
        # Mostrar el gráfico
        fig.show()

    except Exception as e:
        print(f"Error al generar el gráfico para {filtro_var}={valor_filtro}: {e}")

# Crear gráficos utilizando las etiquetas:
# 1. Crear gráficos para cada valor de la variable 'sexo'
for sexo in df_filtered['sexo'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'sexo', sexo, sexo_labels,
                            f"Tendencia de Desocupación para {sexo_labels[sexo]}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_{sexo_labels[sexo]}.pdf')

# 2. Crear gráficos para cada tramo de edad
for tramo in df_filtered['tramo_edad'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'tramo_edad', tramo, tramo_edad_labels,
                            f"Tendencia de Desocupación para Tramo de Edad {tramo_edad_labels[tramo]}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_tramo_edad_{tramo_edad_labels[tramo]}.pdf')

# 3. Crear gráficos para Proveedores desocupados
for proveedor in df_filtered['proveedor'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'proveedor', proveedor, proveedor_labels,
                            f"Tendencia de Desocupación para Proveedor {proveedor_labels.get(proveedor, 'Desconocido')}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_proveedor_{proveedor_labels.get(proveedor, "Desconocido")}.pdf')

# 4. Crear gráficos para Nivel Educativo (CINE)
for cine in df_filtered['cine'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'cine', cine, cine_labels,
                            f"Tendencia de Desocupación por Nivel Educativo {cine_labels.get(cine, 'Desconocido')}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_nivel_educativo_{cine_labels.get(cine, "Desconocido")}.pdf')

# 5. Crear gráficos para Cotización Previsional
for cotizacion in df_filtered['b7a_1'].dropna().unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'b7a_1', cotizacion, cotizacion_labels,
                            f"Tendencia de Cotización Previsional {cotizacion_labels.get(cotizacion, 'Desconocido')}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_cotizacion_previsional_{cotizacion_labels.get(cotizacion, "Desconocido")}.pdf')

# 6. Crear gráficos para Estado Civil
for estado in df_filtered['est_conyugal'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'est_conyugal', estado, estado_civil_labels,
                            f"Tendencia de Desocupación por Estado Civil {estado_civil_labels[estado]}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_estado_civil_{estado_civil_labels[estado].replace("/", "_").replace("\\", "_")}.pdf')

# 7. Crear gráficos para Tipo de Estrato
for tipo in df_filtered['tipo'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'tipo', tipo, tipo_labels,
                            f"Tendencia de Desocupación por Estrato {tipo_labels[tipo]}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_tipo_estrato_{tipo_labels[tipo]}.pdf')

# 8. Crear gráficos para Categoría Ocupacional
for categoria in df_filtered['categoria_ocupacion'].unique():
    crear_grafico_por_valor(df_filtered, 'year_month', 'frequency', 'categoria_ocupacion', categoria, categoria_ocupacion_labels,
                            f"Tendencia de Desocupación por Categoría Ocupacional {categoria_ocupacion_labels[categoria]}",
                            {'year_month': 'Fecha', 'frequency': 'Frecuencia'},
                            f'tendencia_desocupacion_categoria_ocupacion_{categoria_ocupacion_labels[categoria]}.pdf')
