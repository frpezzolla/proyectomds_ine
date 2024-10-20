import plotly.graph_objects as go

def plot_series_comparison(data, title, series1_name, series2_name):
    """
    Grafica dos series de tiempo para su comparación.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data[series1_name], mode='lines', name=series1_name, line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data[series2_name], mode='lines', name=series2_name, line=dict(color='orange')))
    
    fig.update_layout(title=title, xaxis_title="Fecha", yaxis_title="Tasa (%)", template='plotly_dark')
    fig.show()

def plot_error(data, error_column, title):
    """
    Grafica el error (diferencia entre dos series).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data[error_column], mode='lines', name='Error', line=dict(color='red')))
    fig.update_layout(title=title, xaxis_title="Fecha", yaxis_title="Error", template='plotly_dark')
    fig.show()
