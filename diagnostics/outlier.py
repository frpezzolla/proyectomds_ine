from os import path
import pandas as pd
import numpy as np
from statsmodels.tsa.x13 import x13_arima_analysis
from statsmodels.tsa.statespace.sarimax import SARIMAX
from plotly import graph_objects as go
import warnings
from statsmodels.tools.sm_exceptions import X13Warning, ConvergenceWarning, ValueWarning, ModelWarning
from sklearn.metrics import mean_squared_error
from x13_diags import SlidingSpans, RevisionHistory


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


class SlidingOutliers(SlidingSpans):
    def MM_mse(self, serie:pd.Series, outlier:pd.Series):
        start = outlier.index[0]
        self.fit(serie[:start], inverse=True)
        preMM = self.MM_ratio().loc[:start, 'metric'].copy()
        self.fit(serie, inverse=True)
        posMM = self.MM_ratio().loc[:start, 'metric'].copy()
        MM = pd.concat([preMM, posMM], axis=1).dropna(how='any', axis=0)
        return mean_squared_error(MM.iloc[:,1], MM.iloc[:,0])

    def A_mse(self, serie:pd.Series, outlier:pd.Series):
        start = outlier.index[0]
        self.fit(serie[:start], inverse=True)
        preA = self.A_ratio().loc[:start, 'metric'].copy()
        self.fit(serie, inverse=True)
        posA = self.A_ratio().loc[:start, 'metric'].copy()
        A = pd.concat([preA, posA], axis=1).dropna(how='any', axis=0)
        return mean_squared_error(A.iloc[:,1], A.iloc[:,0])
    
    def MM_analysis(self, serie:pd.Series, outlier:pd.Series):
        start = outlier.index[0]
        self.fit(serie[:start], inverse=True)
        preMM = self.MM_ratio().loc[:start, 'metric'].copy()
        preMM_percentage = self.predict()['MM%']
        self.fit(serie, inverse=True)
        posMM = self.MM_ratio().loc[:start, 'metric'].copy()
        posMM_percentage = self.predict()['MM%']
        return {'preMM': preMM, 'preMM_percentage': preMM_percentage, 'posMM': posMM, 'posMM':posMM_percentage}

    def A_analysis(self, serie:pd.Series, outlier:pd.Series):
        start = outlier.index[0]
        self.fit(serie[:start], inverse=True)
        preA = self.A_ratio().loc[:start, 'metric'].copy()
        preA_percentage = self.predict()['A%']
        self.fit(serie, inverse=True)
        posA = self.A_ratio().loc[:start, 'metric'].copy()
        posA_percentage = self.predict()['A%']
        return {'preA': preA, 'preA_percentage': preA_percentage, 'posA': posA, 'posA':posA_percentage}

        
class RevisionOutlier(RevisionHistory):
    def A_analysis(self, outlier:pd.Series, n_seasons=4):
        if isinstance(self.A, pd.DataFrame):
            a = self.A.copy()
            start, end = outlier.index[0], outlier.index[-1]
            seasons = [start + pd.DateOffset(months=int(12*s)) for s in range(n_seasons)]
            seasons = sorted([*seasons, end])
            achange_base = a.loc[:start, f'A*|[{start.date().isoformat()}]'].copy()
            residue = dict()
            for season in seasons:
                col_target = f'A*|[{season.date().isoformat()}]'
                if col_target in a.columns:
                    achange_target = a.loc[:start, col_target]
                    residue[season] = mean_squared_error(
                        achange_target / achange_base, 
                        np.ones_like(achange_base.to_numpy())
                        )
                else:
                    warnings.warn("Se definen más estaciones de las encontradas en la serie") 
                    break                   
            return pd.Series(residue)
        else:
            raise Exception("Es necesario aplicar método fit a serie")
        
    def C_analysis(self, outlier:pd.Series, n_seasons=4):
        if isinstance(self.C, pd.DataFrame):
            c = self.C.copy()
            start, end = outlier.index[0], outlier.index[-1]
            seasons = [start + pd.DateOffset(months=int(12*s)) for s in range(n_seasons)]
            seasons = sorted([*seasons, end])
            c_base = c.loc[:start, f'C*|[{start.date().isoformat()}]'].copy()
            residue = dict()
            for season in seasons:
                col_target = f'C*|[{season.date().isoformat()}]'
                if col_target in c.columns:
                    c_target = c.loc[:start, col_target]
                    residue[season] = mean_squared_error(c_target, c_base)
                else:
                    warnings.warn("Se definen más estaciones de las encontradas en la serie")      
                    break
            return pd.Series(residue)
        else:
            raise Exception("Es necesario aplicar método fit a serie")
    

if __name__=='__main__':
    from plotly import express as px
    # print(type(str(check_format("2024/10/12"))))
    # s = pd.Series(np.sin(np.linspace(0, 50, 160) + 2)+ 3*np.cos(np.linspace(0, 100, 160) + 0.6*np.random.randn(160)))
    # s.index = pd.date_range(start="2010-09-01", freq="MS", periods=len(s))

    tasa = pd.read_csv("./data/endogena/to202406.csv")
    tasa.index = pd.DatetimeIndex(tasa.pop('ds'))

    # # ss = SlidingSpans(x13_arima_analysis, sliding_len=8, span_len=60)
    # # # ss.fit(tasa.loc['2020-01-01':])
    # # # print(ss.A)
    # # print(ss.A_ratio().tail(10))
    # # print(ss.MM_ratio().tail(10))
    # # print(ss.predict())

    # rh = RevisionHistory(x13_arima_analysis)
    # print(rh.fit(tasa).A)
    # # print(rh.A[f'A*|[{rh.T.date()}]'])
    # print(rh.R_value("20181001"))
    # print(rh.C)

    ro = RevisionOutlier(x13_arima_analysis)
    outlier = pd.Series(pd.date_range(start='2020-01-01', end='2022-05-01', freq='MS'))
    outlier.index = pd.DatetimeIndex(outlier)
    outlier.loc[:] = 1
    ro.fit(tasa)
    change = ro.A_analysis(outlier=outlier, n_seasons=9)
    fig = px.line(change)
    fig.show()
    
    change = ro.C_analysis(outlier=outlier, n_seasons=9)
    fig = px.line(change)
    fig.show()

    sli = SlidingOutliers(x13_arima_analysis)
    print(sli.A_analysis(serie=tasa, outlier=outlier))
    print(sli.MM_analysis(serie=tasa, outlier=outlier))







