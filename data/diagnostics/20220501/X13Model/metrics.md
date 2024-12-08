## Diagnósticos para X13Model, respecto a outlier 2020-01-01|2022-05-01

            
Contraste de entrenamiento entre modelo con datos hasta la pandemia (2020-01-01), y modelo con datos hasta último registro
            
Diagnostivo Slidings Spans. MSE entre valores A\% para los dos modelos, de la forma
$$\frac{max_j A_t^j - min_j A_t^j}{min_j A_t^j}$$
            **MSE**: 0.00023887263495692328


Diagnostivo Slidings Spans. MSE entre valores MM\% para los dos modelos, de la forma
$$max_j \frac{A_t^j}{A_{t-1}^j} - min_j \frac{A_t^j}{A_{t-1}^j}$$
                       **MSE**: 7.574486440320408e-05

**Test A%** pre-pandemia: 1.0
**Test A%** todos los datos: 0.722
**Test MM%** pre-pandemia: 1.0
**Test MM%** todos los datos: 0.944
