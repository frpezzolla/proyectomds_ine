from pandas import Series
from statsmodels.tsa.x13 import x13_arima_analysis, X13Error
import os
from os import path
from models.base import BaseModel
import traceback


x13as_path = os.getenv('X13PATH')
class X13Model(BaseModel):
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
        except X13Error as e:
            raise e
        except Exception as e:
            print(type(e).__name__, traceback.format_exc(), sep=': ')
            raise ValueError("Required model hiperparameters missing")
        self._seasadj = self.model_obj.seasadj.rename('seasadj')
        return self

if __name__=='__main__':
    asdf = X13Model(hiperparams={})
    print(asdf.__name__)
    asdf.adjust()
    print(asdf.seasadj)
    pass