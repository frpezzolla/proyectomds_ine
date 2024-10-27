from os import path
import pandas as pd
from statsmodels.tsa.x13 import x13_arima_analysis
from statsmodels.tsa.statespace.sarimax import SARIMAX
from plotly import graph_objects as go
import warnings
from statsmodels.tools.sm_exceptions import X13Warning, ConvergenceWarning, ValueWarning, ModelWarning
from sklearn.metrics import mean_squared_error

warnings.simplefilter('ignore', category=X13Warning)
warnings.simplefilter('ignore', category=ConvergenceWarning)
warnings.simplefilter('ignore', category=UserWarning)
warnings.simplefilter('ignore', category=ValueWarning)


x13as_path = path.abspath("C:/Program Files/x13as")
class OutlierAnalysis():
    """
    Analyze an 
    :params: 
    :returns:
    """
    def __init__(self, time_serie:pd.Series, start_date:pd.Timestamp=None, end_date:pd.Timestamp=None, forecast_model=SARIMAX, exogenous=[]) -> None:
        self.serie = time_serie
        self.comp_serie = None
        self.comp_adj = None
        self.real_adj = None
        self.start = start_date
        self.end = end_date
        self.forecast_model = forecast_model
        self.outlier_period = (self.end.year-self.start.year)*12 + (self.end.month - self.start.month)

    def forecast(self, periods, serie=None, model=None):
        serie = self.serie if serie is None else serie
        model = self.forecast_model if model is None else model

        if model.__name__=='SARIMAX':
            sari = model(
                endog=serie,
                order=(4,1,4),
                seasonal_order=(2,1,2,12),
                freq='MS'
                )
            results = sari.fit()
            if periods > 0:
                fore = results.forecast(steps=periods)

        return fore

    def compose_serie(self, model, serie=None):
        serie = self.serie if serie is None else serie
        model = self.forecast_model if model is None else model

        pre_out = serie.loc[:self.start].copy()
        post_out = serie.loc[self.end:].copy()
        
        # Modelo SARIMAX para predecir periodo pandemia
        fore = self.forecast(self.outlier_period, pre_out, model)
        comp_serie = pre_out.reindex(serie.index)
        comp_serie = comp_serie.fillna(fore).fillna(post_out)

        self.comp_serie = comp_serie if serie is None else self.comp_serie
        return comp_serie
    
    def seasonality_diff(self, seasonal_model=x13_arima_analysis, serie=None,  forecast_model=None, mse_limit=None):
        serie = self.serie if serie is None else serie
        forecast_model = self.forecast_model if forecast_model is None else forecast_model

        comp_serie = self.compose_serie(forecast_model, serie)
        
        # Modelo X13-SARIMA
        # Desestacionalización Serie compuesta por parte OFICIAL-PRONOSTICO-OFICIAL (Prepandemia-Pandemia-Pospandemia)
        if seasonal_model.__name__== 'x13_arima_analysis':
            x13comp = seasonal_model(
                endog=comp_serie,
                maxorder=(1,1),
                x12path=x13as_path,
                outlier=False)
            # Predicción Serie Oficial
            x13real = seasonal_model(
                endog=serie,
                maxorder=(1,1),
                x12path=x13as_path,
                outlier=False)
        
            comp_adj = x13comp.seasadj
            real_adj = x13real.seasadj
            self.comp_adj = comp_adj if serie is None else self.comp_adj
            self.real_adj = real_adj if serie is None else self.real_adj

        mse_limit = slice(mse_limit)
        model_diff = mean_squared_error(comp_adj.loc[mse_limit], real_adj.loc[mse_limit]) # MSE sin contabilizar directamente nuevos datos
        print("MSE para desestacionalización Tasa compuesta y Tasa real: ", model_diff)
        
        return model_diff
    

    def plot(self, mode):
        plots = {
            'composed':go.Scatter(x=self.comp_serie.index, y=self.comp_serie, name='Composed'), 
            'real':go.Scatter(x=self.serie.index, y=self.serie, name='Real'), 
            'adjusted composed':go.Scatter(x=self.comp_adj.index, y=self.comp_adj, name='Adjusted Composed'),
            'adjusted real':go.Scatter(x=self.real_adj.index, y=self.real_adj, name='Adjusted Real'),
            'adjusted diff':go.Scatter(x=self.real_adj.index, y=self.real_adj-self.comp_adj, name='Difference on Adjustment'),
            'diff':go.Scatter(x=self.serie.index, y=self.serie-self.comp_serie, name='Real Difference')
            }
        fig = go.Figure()
        if mode=='all':
            for n, p in plots.items():
                fig.add_traces(p)
        elif mode=='adjusted':
            for n, p in plots.items():
                if 'adjusted' in n and 'diff' not in n:
                    fig.add_traces(p)
        elif mode=='normal':
            for n, p in plots.items():
                if 'adjusted' not in n and 'diff' not in n:
                    fig.add_traces(p)
        elif mode=='diff':
            for n, p in plots.items():
                if 'adjusted' not in n and 'diff' in n:
                    fig.add_traces(p)
        else:
            fig.add_traces(plots[mode])
    
    def model_evolution(self, seasonal_model=x13_arima_analysis):
        self.mses = []
        last_date = self.end
        while last_date in self.serie.index:
            cropped = self.serie[:last_date + pd.DateOffset(months=1)]
            self.mses.append(self.seasonality_diff(serie=cropped, seasonal_model=seasonal_model, mse_limit=self.start))
            last_date = last_date + pd.DateOffset(months=1)
    
    def plot_evol(self):
        fig = go.Figure(go.Scatter(x=self.serie[self.end:].index, y=self.mses))
        fig.show()