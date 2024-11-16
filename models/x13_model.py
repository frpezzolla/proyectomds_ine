from statsmodels.tsa.x13 import x13_arima_analysis
from os import path
from base import BaseModel

x13as_path = path.abspath("C:/Program Files/x13as")
class X13Wrap(BaseModel):
    def adjust(self):
        self.model_obj = x13_arima_analysis(
            endog=self.endog,
            exog=self.exog,
            order=self.hiperparams.get('order'),
            seasonal_order=self.hiperparams.get('seasonal_order'),
            freq=self.hiperparams.get('freq'),
            outlier=self.hiperparams.get('outlier')
        )
        return self


if __name__=='__main__':
    # asdf = X13Wrap()
    pass