# Paquetes
import plotly.graph_objects as go

# Función que grafica series de tiempo en el dataframe entregado
# con su índice una columna de fechas secuenciales en formato date time.
# Se deben  entregar los índices de las columnas a graficar en una lista
# en el argumento indexes.
def plot_series(dataframe, indexes=[], title='Series de Tiempo', x_label='Fecha', y_label='Valor', colors=None):
    """
    Función para graficar series de tiempo de un DataFrame con su índice como una columna de fechas en formato datetime.
    
    Parámetros:
    - dataframe (pd.DataFrame): DataFrame con los datos y fechas como índice.
    - indexes (list): Lista de columnas a graficar.
    - title (str): Título del gráfico.
    - x_label (str): Etiqueta del eje X.
    - y_label (str): Etiqueta del eje Y.
    - colors (list): Lista de colores para cada serie, opcional.
    """

    columns = dataframe.columns.tolist()
    # Error de columnas entregadas no disponibles en el dataframe
    missing_columns = [col for col in indexes if col not in columns]
    if missing_columns:
        raise ValueError(f"Las columnas {missing_columns} no existen en el DataFrame.")
    
    # Creamos la figura
    fig = go.Figure()

    # Colores default
    if colors is None:
        colors = ['royalblue', 'green', 'firebrick', 'orange', 'purple']

    for i,column in enumerate(indexes):
        color = colors[i % len(colors)]  # Asignar color, repetir si faltan colores
        # Agregamos la serie de tiempo correspondiente
        fig.add_trace(go.Scatter(
            # Índice 'date' del DataFrame
            x=dataframe.index,
            # Serie de tiempo  
            y=dataframe[column],
            # Tipo de marca
            mode='lines+markers',
            # Nombre de la serie
            name=column,
            # Personalización del color y grosor de línea
            line=dict(color=color, width=2),  
            # Tamaño de los puntos
            marker=dict(size=4)  
            ))
    # Actualizar layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend=dict(
            title='Variables',
            x=0.02, y=0.98,  # Posición de la leyenda en el gráfico
            bgcolor='rgba(255, 255, 255, 0.5)'  # Fondo semi-transparente de la leyenda
        ),
        template='plotly_white'
    )
    fig.show()