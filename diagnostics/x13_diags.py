from os import path
import pandas as pd
import numpy as np
from statsmodels.tsa.x13 import x13_arima_analysis
from statsmodels.tsa.statespace.sarimax import SARIMAX
from plotly import graph_objects as go
import warnings
from statsmodels.tools.sm_exceptions import X13Warning, ConvergenceWarning, ValueWarning, X13Error
from sklearn.metrics import mean_squared_error

from models.base import BaseModel

# from ..tools.exceptions import FormatoFechaError
warnings.simplefilter('ignore', category=X13Warning)
warnings.simplefilter('ignore', category=ConvergenceWarning)
warnings.simplefilter('ignore', category=UserWarning)
warnings.simplefilter('ignore', category=ValueWarning)


def check_format(date):
    if isinstance(date, pd.Timestamp): 
        return date
    allowed_format = ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]
    error = None
    for format in allowed_format:
        try:
            return pd.to_datetime(str(date), format=format)
        except ValueError as e:
            error = e
    else:
        raise error

x13as_path = path.abspath("C:/Program Files/x13as")
class SlidingSpans():
    # Considero mejor definir el modelo en el init, es decir, por objecto, a diferencia de outlier.OutlierAnalysis
    def __init__(self, model:BaseModel, sliding_len=12, span_len=48) -> None:
        self.model = model
        self.sliding_len = sliding_len
        self.span_len = span_len
        self.A = None
        self._A_ratio, self._MM_ratio = None, None
        self.A_metric, self.MM_metric = None, None

    def fit(self, serie:pd.Series, inverse=False):
        origin = serie.copy()
        A = pd.DataFrame(index=origin.index)
        if not inverse:
            slide_iter = range(0, len(origin.index)-self.span_len, self.sliding_len)
            j_sets = iter(origin.iloc[j_index:j_index+self.span_len].copy() for j_index in slide_iter)
        else:
            slide_iter = range(len(origin.index), self.span_len, -self.sliding_len)
            j_sets = iter(origin.iloc[j_index-self.span_len:j_index].copy() for j_index in slide_iter)

        # for n, j_index in enumerate(range(0, len(origin.index)-self.span_len, self.sliding_len)):
            # j_set = origin.iloc[j_index:j_index+self.span_len].copy()
        for n, j_set in enumerate(j_sets):   
            try:
                self.model.fit(endog=j_set)
                x13j = self.model.adjust()
                # if self.model.__name__== 'x13_arima_analysis':
                    # x13j = self.model(
                    #     endog=j_set,
                    #     maxorder=(1,1),
                    #     x12path=x13as_path,
                    #     outlier=False)
                Aj = x13j.seasadj.rename(f'A^{n+1}')
                A = pd.concat([A, Aj], axis=1)
            except X13Error as e:
                X13Error("Para modelo X13 span_len debe ser 36 o superior (más de 3 años) ")
        if A.empty or len(A.columns)<2:
            raise X13Error("Serie debe ser de 3 años o más para desestacionalizar con X13 y para realizar diagnóstico")
        self.A = A.replace(np.nan, pd.NA)
        return self
    
    def min(self, serie:pd.Series):
         serie = serie.dropna()
         return serie.min() if len(serie)>1 else pd.NA

    def max(self, serie:pd.Series):
         serie = serie.dropna()
         return serie.max() if len(serie)>1 else pd.NA

    def A_ratio(self, threshold=0.03):
        A_ratio = pd.DataFrame()
        if isinstance(self.A, pd.DataFrame) and not self.A.empty:
            maxA = self.A.aggregate(self.max, axis=1)
            minA = self.A.aggregate(self.min, axis=1)
            A_ratio['metric'] = (maxA - minA) / minA
            A_ratio['success'] = A_ratio['metric'] < threshold
            self._A_ratio = A_ratio.dropna(axis=0, how='any')
            return self._A_ratio
        
        else:
            raise Exception("The diagnostic must be fit before calling A ratio")
        
    def MM_ratio(self, threshold=0.03):
        MM_ratio = pd.DataFrame()
        if isinstance(self.A, pd.DataFrame) and not self.A.empty:
            MM = self.A / self.A.shift(1)
            maxMM = MM.aggregate(self.max, axis=1)
            minMM = MM.aggregate(self.min, axis=1)
            MM_ratio = pd.DataFrame()
            MM_ratio['metric'] = maxMM - minMM
            MM_ratio['success'] = MM_ratio['metric'] < threshold 
            self._MM_ratio = MM_ratio.dropna(axis=0, how='any')
            return self._MM_ratio
        
        else:
            raise Exception("The diagnostic must be fit before calling A ratio")
        
    def predict(self):
        self.A_metric = self._A_ratio['success'].sum()/len(self._A_ratio['success'])
        self.MM_metric = self._MM_ratio['success'].sum()/len(self._MM_ratio['success'])
        return {'A%:':self.A_metric, 'MM%': self.MM_metric}

class RevisionHistory():
    def __init__(self, model:BaseModel) -> None:
        self.model = model
        self.A = None
        self.C = None
        self.T = None

    def fit(self, serie:pd.Series):
        origin = serie.copy()
        A = pd.DataFrame(index=origin.index)
        for date_n in serie.index[3:]:
            subserie_n = origin[:date_n]
            try:
                # if self.model.__name__== 'x13_arima_analysis':
                self.model.fit(endog=subserie_n)
                x13j = self.model.adjust()
                    # x13j = self.model(
                    #     endog=subserie_n,
                    #     maxorder=(1,1),
                    #     x12path=x13as_path,
                    #     outlier=False)
                An = x13j.seasadj.rename(f'A*|[{date_n.date()}]')
                A = pd.concat([A, An], axis=1)
            except X13Error as e:
                pass
        if A.empty or len(A.columns)<2:
            raise X13Error("Serie muy corta para relizar diagnóstico")
        self.A = A.replace(np.nan, pd.NA).copy()
        self.C = ((self.A - self.A.shift(1)) / self.A.shift(1)).replace(np.nan, pd.NA).dropna(how='all', axis=0).copy()
        self.C.columns = pd.Series(self.A.columns).apply(lambda name: name.replace('A', 'C'))
        self.T = origin.index[-1]
        return self
    
    def _A_n(self, n):
        n = check_format(n)
        if n.day != 1: raise ValueError(f"Columna empieza con el primer día del mes. Fecha entregada: {n.date()}")
        return self.A[f'A*|[{n.date()}]'].copy()
    
    def _C_n(self, n):
        n = check_format(n)
        if n.day != 1: raise ValueError(f"Columna empieza con el primer día del mes. Fecha entregada: {n.date()}")
        return self.C[f'C*|[{n.date()}]'].copy()

    def A_change(self, n_final, n_init):
        A_init = self._A_n(n_init)
        return (self._A_n(n_final) - A_init) / A_init
    
    def C_change(self, n_final, n_init):
        return self._C_n(n_final) - self._C_n(n_init)

    def R_value(self, t):
        return self.A_change(self.T, t).iloc[-1]


if __name__=='__main__':
    # print(type(str(check_format("2024/10/12"))))
    # s = pd.Series(np.sin(np.linspace(0, 50, 160) + 2)+ 3*np.cos(np.linspace(0, 100, 160) + 0.6*np.random.randn(160)))
    # s.index = pd.date_range(start="2010-09-01", freq="MS", periods=len(s))

    tasa = pd.read_csv("./data/endogena/to202406.csv")
    tasa.index = pd.DatetimeIndex(tasa.pop('ds'))

    ss = SlidingSpans(x13_arima_analysis, sliding_len=8, span_len=60)
    ss.fit(tasa, inverse=True)
    # print(ss.A)
    print(ss.A_ratio())
    print(ss.MM_ratio())
     
    print(ss.predict())

    ss.fit(tasa[:'2020-01-01'], inverse=True)
    # print(ss.A)
    print(ss.A_ratio())
    print(ss.MM_ratio())
     
    print(ss.predict())

    # rh = RevisionHistory(x13_arima_analysis)
    # print(rh.fit(tasa).A)
    # # print(rh.A[f'A*|[{rh.T.date()}]'])
    # print(rh.R_value("20181001"))
    # print(rh.C)