from diagnostics import outlier_analysis as oa
import pandas as pd
import os
from os.path import join, realpath
import logging
class Diagnose():
    def __init__(self, serie) -> None:
        self.serie = serie

    def set_outlier(self, outlier_serie:pd.Series):
        self.outlier = outlier_serie
        self.outlier = self.outlier.loc[self.outlier == 1]
        self.start = outlier_serie.index[0].date().isoformat()
        self.end = outlier_serie.index[-1].date().isoformat()
    
    def diags(self,  model):
        pass

    def outlier_diags(self, model):
        logging.info(f"Running diagnostics for {model.__name__}")
        out_analist = oa.OutlierAnalysis()    
        span_analist = oa.SlidingOutliers(model())
        history_analist = oa.RevisionOutlier(model())

        results_path = join(realpath('.'), 'data', 'diagnostics', self.end.replace('-', ''), model.__name__)
        os.makedirs(results_path, exist_ok=True)
        
        out_analist.fit(self.serie, outlier=self.outlier)
        instance_model = model()
        out_analist.model_evolution(instance_model).to_csv(join(results_path, 'mse_comp_real.csv'))

        with open(join(results_path,'metrics.md'), 'w', encoding='utf-8') as file:
            file.write(f"""## Diagnósticos para {model.__name__}, respecto a outlier {self.start}|{self.end}

            """)
            file.write(f"""
Contraste de entrenamiento entre modelo con datos hasta la pandemia ({self.start}), y modelo con datos hasta último registro
            """)
            file.write(
"Diagnostivo Slidings Spans. MSE entre valores A\% para los dos modelos, de la forma"
"$$\\frac{max_j A_t^j - min_j A_t^j}{min_j A_t^j}$$")
            mse = f"**MSE**: {str(span_analist.A_mse(self.serie, outlier=self.outlier))}\n\n"
            file.write(mse)
            file.write(
"Diagnostivo Slidings Spans. MSE entre valores MM\% para los dos modelos, de la forma"
"$$max_j \\frac{A_t^j}{A_{t-1}^j} - min_j \\frac{A_t^j}{A_{t-1}^j}$$")
            mse = f"**MSE**: {str(span_analist.MM_mse(self.serie, outlier=self.outlier))}\n\n"
            file.write(mse)
            saa = span_analist.A_analysis(self.serie, outlier=self.outlier)
            smma = span_analist.MM_analysis(self.serie, outlier=self.outlier)
            test = f"**Test A%** pre-pandemia: {round(saa['pre_percentage'], 3)}\n"
            file.write(test)
            test = f"**Test A%** todos los datos: {round(saa['pos_percentage'], 3)}\n"
            file.write(test)
            test = f"**Test MM%** pre-pandemia: {round(smma['pre_percentage'], 3)}\n"
            file.write(test)
            test = f"**Test MM%** todos los datos: {round(smma['pos_percentage'], 3)}\n"
            file.write(test)

        saa['pre'].to_csv(join(results_path, 'A%_pre.csv'))
        saa['pos'].to_csv(join(results_path, 'A%_pos.csv'))

        smma['pre'].to_csv(join(results_path, 'MM%_pre.csv'))
        smma['pos'].to_csv(join(results_path, 'MM%_pos.csv'))


        history_analist.fit(self.serie)
        history_analist.A_analysis(outlier=self.outlier).to_csv(join(results_path, 'RY.csv'))
        history_analist.C_analysis(outlier=self.outlier).to_csv(join(results_path, 'CY.csv'))