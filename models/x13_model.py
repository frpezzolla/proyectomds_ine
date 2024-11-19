from pandas import Series
from statsmodels.tsa.x13 import x13_arima_analysis
from os import path
from models.base import BaseModel
import traceback

x13as_path = path.abspath("C:/Program Files/x13as")
class X13Wrap(BaseModel):
    def __init__(self, hiperparams:dict={'maxorder':(1,1), 'outlier':False}) -> None:
        super().__init__(hiperparams)
        
    def adjust(self):
        try:
            self.model_obj = x13_arima_analysis(
                endog=self.endog,
                exog=self.exog,
                maxorder=self.hiperparams.get('maxorder'),
                x12path=x13as_path,
                outlier=self.hiperparams.get('outlier'),
            )
        except Exception as e:
            print(type(e).__name__, traceback.format_exc(), sep=': ')
            raise ValueError("Faltan hiperparámetros requeridos por el modelo")
        self._seasadj = self.model_obj.seasadj.rename('seasadj')
        return self
    
    @property
    def __name__(self):
        return x13_arima_analysis.__name__


if __name__=='__main__':
    asdf = X13Wrap(hiperparams={})
    print(asdf.__name__)
    asdf.adjust()
    print(asdf.seasadj)
    pass