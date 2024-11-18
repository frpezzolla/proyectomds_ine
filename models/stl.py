# Importamos clase plantilla
from models.base import BaseModel

# Paquetes
from statsmodels.tsa.seasonal import STL
import pandas as pd

# Definimos la subclase
class STLModel(BaseModel):
    # Inicializador
    def __init__(self, hiperparams: dict, outlier: pd.Series = None) -> None:
        # Herencia de características
        super().__init__(hiperparams, outlier)
        # Guardar el resultado
        self._stl_result = None

    def adjust(self) -> pd.Series:
        """
        Ajusta la serie eliminando la componente estacional utilizando STL.
        Guarda la serie ajustada en self._seasadj.
        """
        if self.endog is None:
            raise ValueError("Debe llamar al método fit con una serie antes de ajustar.")
        
        # Configurar STL con hiperparámetros
        stl = STL(self.endog, **self.hiperparams)
        # Ajustamos y guardamos en la variable correspondiente
        self._stl_result = stl.fit()

        # Calcular la serie ajustada (tendencia + residuo)
        self._seasadj = self._stl_result.trend + self._stl_result.resid
        return self._seasadj

    def trend_cycle(self) -> pd.Series:
        """
        Devuelve la componente de tendencia-ciclo de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self._stl_result is None:
            raise ValueError("Debe llamar al método adjust antes de obtener la tendencia.")
        # Retornamos
        return self._stl_result.trend

    def seasonality(self) -> pd.Series:
        """
        Devuelve la componente estacional de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self._stl_result is None:
            raise ValueError("Debe llamar al método adjust antes de obtener la estacionalidad.")
        # Retornamos
        return self._stl_result.seasonal

    def residue(self) -> pd.Series:
        """
        Devuelve la componente de residuo de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self._stl_result is None:
            raise ValueError("Debe llamar al método adjust antes de obtener el residuo.")
        # Retornamos
        return self._stl_result.resid

# --------------------------------------------------------------------------------------------------
# Ejemplo de uso
# --------------------------------------------------------------------------------------------------
if __name__=='__main___':
    pass
    # Diccionario de hiperparámetros
    #hiperparams = {'seasonal': 13, 'robust': True}

    # Instanciamos
    #stl_model = STLModel(hiperparams)

    # Leemos la base y la formateamos

    #data = pd.read_csv("./Datos/processed/desocupacion.csv")
    #data.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
    #data.index = pd.to_datetime(data["date"])
    #data=data.drop(["date"],axis=1)


    # Entrenar el modelo
    #stl_model.fit(endog=data['Tasa oficial'])

    # Ajustar y obtener la serie desestacionalizada
    #serie_desestacionalizada = stl_model.adjust()

    # Obtener componentes específicas
    #tendencia = stl_model.trend_cycle()
    #estacionalidad = stl_model.seasonality()
    #residuo = stl_model.residue()

    #print(pd.DataFrame({"STL desestacionalizada":serie_desestacionalizada,"Ajustada INE":data["Tasa ajustada"]}))





