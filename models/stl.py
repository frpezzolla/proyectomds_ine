# Importamos clase plantilla
from models.base import BaseModel #models.base

# Paquetes
from statsmodels.tsa.seasonal import STL
import pandas as pd

# Definimos la subclase
class STLModel(BaseModel):
    # Inicializador
    def __init__(self, hiperparams = {'seasonal': 13, 'robust': True}) -> None:
        # Herencia de características
        super().__init__(hiperparams)
        

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
        self.model_obj = stl.fit()

        # Calcular la serie ajustada (tendencia + residuo)
        self._seasadj = self.model_obj.trend + self.model_obj.resid
        return self

    def trend_cycle(self) -> pd.Series:
        """
        Devuelve la componente de tendencia-ciclo de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self.model_obj is None:
            raise ValueError("Debe llamar al método adjust antes de obtener la tendencia.")
        # Retornamos
        return self.model_obj.trend

    def seasonality(self) -> pd.Series:
        """
        Devuelve la componente estacional de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self.model_obj is None:
            raise ValueError("Debe llamar al método adjust antes de obtener la estacionalidad.")
        # Retornamos
        return self.model_obj.seasonal

    def residue(self) -> pd.Series:
        """
        Devuelve la componente de residuo de la serie ajustada.
        """
        # Nos aseguramos de haber llamado a adjust
        if self.model_obj is None:
            raise ValueError("Debe llamar al método adjust antes de obtener el residuo.")
        # Retornamos
        return self.model_obj.resid

# --------------------------------------------------------------------------------------------------
# Ejemplo de uso
# --------------------------------------------------------------------------------------------------
#if __name__=='__main___':
    #pass

    # Instanciamos
    #stl_model = STLModel()

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





