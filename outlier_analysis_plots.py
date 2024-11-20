from plotly import graph_objects as go
import pandas as pd

rt = "./data/diagnostics/"
x13_oamse = pd.read_csv(rt+"/X13Model_out20220501/mse_comp_real.csv")
stl_oamse = pd.read_csv(rt+"/STLModel_out20220501/mse_comp_real.csv")
cissa_oamse = pd.read_csv(rt+"/CiSSAModel_out20220501/mse_comp_real.csv")
go.Figure(go.Scatter())