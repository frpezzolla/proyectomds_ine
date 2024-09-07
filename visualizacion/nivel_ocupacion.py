import os
import pandas as pd
import plotly.express as px

data = pd.read_excel(io="./data/ine/ajuste_estacional.xlsx", sheet_name="tasa_as", header=[5,6])
data = data.loc[:172]
data.columns = data.columns.get_level_values(0)
# data.set_index(["Año", "Trimestre"], inplace=True)
data["Año, Trimestre"] = data[["Año", "Trimestre"]].aggregate(lambda x: ", ".join(x.astype(str)), axis=1)

fig = px.line(data, x="Año, Trimestre", y=["Tasa oficial", "Tasa ajustada"], markers=True)
fig.show()
# fig.write_image("./visualizacion/plots/tasas.png")