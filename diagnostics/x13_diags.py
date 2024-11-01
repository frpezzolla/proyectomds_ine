from os import path
import pandas as pd
import numpy as np
from statsmodels.tsa.x13 import x13_arima_analysis
from statsmodels.tsa.statespace.sarimax import SARIMAX
from plotly import graph_objects as go
import warnings
from statsmodels.tools.sm_exceptions import X13Warning, ConvergenceWarning, ValueWarning, X13Error
from sklearn.metrics import mean_squared_error

warnings.simplefilter('ignore', category=X13Warning)
warnings.simplefilter('ignore', category=ConvergenceWarning)
warnings.simplefilter('ignore', category=UserWarning)
warnings.simplefilter('ignore', category=ValueWarning)

x13as_path = path.abspath("C:/Program Files/x13as")
class SlidingSpans():
    # Considero mejor definir el modelo en el init, es decir, por objecto, a diferencia de outlier.OutlierAnalysis
    def __init__(self, model, sliding_len=6, span_len=48) -> None:
        self.model = model
        self.sliding_len = sliding_len
        self.span_len = span_len
        self.A = None
        self._A_ratio, self._MM_ratio = None, None
        self.A_metric, self.MM_metric = None, None

    def fit(self, serie:pd.Series):
        origin = serie.copy()
        A = pd.DataFrame(index=origin.index)
        for n, j_index in enumerate(range(0, len(origin.index)-self.span_len, self.sliding_len)):
            j_set = origin.iloc[j_index:j_index+self.span_len].copy()
            try:
                if self.model.__name__== 'x13_arima_analysis':
                    x13j = self.model(
                        endog=j_set,
                        maxorder=(1,1),
                        x12path=x13as_path,
                        outlier=False)
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
        return self.A_metric, self.MM_metric

class RevisionHistory():
    def __init__(self) -> None:
        pass

if __name__=='__main__':
    s = pd.Series(np.sin(np.linspace(0, 50, 160) + 2)+ 3*np.cos(np.linspace(0, 100, 160) + 0.6*np.random.randn(160)))
    s.index = pd.date_range(start="2010-09-01", freq="MS", periods=len(s))

    tasa = pd.read_csv("./data/endogena/to202406.csv")
    tasa.index = pd.DatetimeIndex(tasa.pop('ds'))

    ss = SlidingSpans(x13_arima_analysis, sliding_len=8, span_len=60)
    ss.fit(tasa.loc['2020-01-01':])

    print(ss.A)
    print(ss.A_ratio().tail(10))
    print(ss.MM_ratio().tail(10))
    print(ss.predict())
