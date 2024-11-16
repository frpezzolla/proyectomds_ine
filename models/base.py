import pandas as pd
from statsmodels.tsa.x13 import x13_arima_analysis


class BaseModel():
    def __init__(self, hiperparams:dict, outlier:pd.Series=None) -> None:
        self.hiperparams = hiperparams
        self.endog = None
        self.exog = None
        self.model_obj = None
        self._seasadj = None

    def fit(self, endog:pd.Series, exog:pd.Series):
        self.endog = endog
        self.exog = exog
        return self
    
    def adjust(self):
        pass

    def trend_cycle(self) -> pd.Series:
        pass

    def seasonality(self) -> pd.Series:
        pass
    
    def residue(self) -> pd.Series:
        pass

    @getattr
    def seasadj(self) -> pd.Series:
        if isinstance(self._seasadj, pd.Series):
            return self._seasadj
        else:
            raise AttributeError("Para obtener serie ajustada debe entrenar el modelo")

    

