from plotly import graph_objects as go
import pandas as pd

generic_layouts = {
    # "legend_title":"Serie temporal:", 
    #    "yaxis_title":"<b>Tasa de Desocupación</b>",
    "xaxis_title":"<b>Fecha</b>",
                   "yaxis_range":[5.5,13.5],
                    "font":dict(
                        family="Courier New, monospace",
                        size=16,
                        color="Black",
                        variant="small-caps"
                        ),
                    "legend":dict(
                        # orientation="h",
                        yanchor="bottom",
                        y=1.0,
                        xanchor="right",
                        x=1.0,
                        bgcolor="LightBlue"
                        )
                    }

rt = "./data/diagnostics/"
x13 = pd.read_csv(rt+"/X13Model_out20220501/mse_comp_real.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/mse_comp_real.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/mse_comp_real.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Comparativa cambio del MSE (Diagnóstico Compuesto-Real) al agregar datos a la serie.",
    yaxis_title="<b>MSE Periodo pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/CY.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/CY.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/CY.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Cambio en MSE Periodo pre-pandemia para diagnóstico Revision History, valor CY.",
    yaxis_title="<b>MSE Periodo pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/RY.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/RY.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/RY.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Cambio en MSE Periodo pre-pandemia para diagnóstico Revision History, valor RY.",
    yaxis_title="<b>MSE Periodo pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/A%_pre.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/A%_pre.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/A%_pre.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Valores A% para cada Modelo en periodo pre-pandemia",
    yaxis_title="<b>Valores de A% pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/MM%_pre.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/MM%_pre.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/MM%_pre.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Valores MM% para cada Modelo en periodo pre-pandemia",
    yaxis_title="<b>Valores de MM% pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/A%_pos.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/A%_pos.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/A%_pos.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Valores A% para cada Modelo. Diagnóstico de todo el periodo ",
    yaxis_title="<b>Valores de A% pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()

x13 = pd.read_csv(rt+"/X13Model_out20220501/MM%_pos.csv")
stl = pd.read_csv(rt+"/STLModel_out20220501/MM%_pos.csv")
cissa = pd.read_csv(rt+"/CiSSAModel_out20220501/MM%_pos.csv")
fig = go.Figure()
fig.add_trace(go.Scatter(x=x13['ds'], y=x13.iloc[:,1], name="X13-ARIMA"))
fig.add_trace(go.Scatter(x=stl['ds'], y=stl.iloc[:,1], name="STL"))
fig.add_trace(go.Scatter(x=cissa['ds'], y=cissa.iloc[:,1], name="CiSSA"))
fig.update_layout(
    title="Valores MM% para cada Modelo. Diagnóstico de todo el periodo ",
    yaxis_title="<b>Valores de MM% pre-pandemia</b>",
    )
fig.update_layout(**generic_layouts)
fig.show()