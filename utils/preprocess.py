import os 
import io
import glob
from os.path import join, realpath
import requests
from calendar import monthrange

import logging
import pandas as pd


class ENE():
    def __init__(self):
        self.data_path = join(realpath('.'), 'data')
        self.raw_path = join(self.data_path, 'raw')
        os.makedirs(self.raw_path, exist_ok=True)
        self.preprocess_path = join(self.data_path, 'preprocess')
        os.makedirs(self.preprocess_path, exist_ok=True)
        self.final_name = 'tasa_oficial.csv'
        
    def groupby_cae(self, tipo):
        if tipo!='anual' and tipo!='mensual':
            raise ValueError("Valores permitidos para tipo son: 'anual', 'mensual'")
        csv_files = glob.glob(join(self.raw_path, tipo if tipo=='anual' else 'monthly', '*.csv'))
        if len(csv_files) == 0:
            return
        # csv_files = [f'./data/ano-{year}.csv' for year in range(2010, 2024)]
        # Añadir los archivos ENE enero-febrero-marzo y abril-mayo-junio de 2024

        date_set = ['ano_encuesta', 'mes_encuesta'] 
        columns = ['ano_trimestre', 'mes_central', 'ano_encuesta', 'mes_encuesta', 'sexo', 'cae_especifico', 'edad']
        agg_nivel = pd.DataFrame()
        # Leemos todos los csv en la lista de una vez, utilizando el sep=';' propio de las ENE trimestrales
        for file in csv_files:
            raw = pd.read_csv(file, usecols=columns, encoding='latin1', sep=';')
            # Convertir a categorías.
            categorical_columns = ['sexo', 'cae_especifico']
            for col in categorical_columns:
                raw[col] = raw[col].astype('category')
            desocupado = self.nivel_estratificado(raw, estado='desocupado', date_set=date_set)
            ocupado  = self.nivel_estratificado(raw, estado='ocupado',  date_set=date_set)
            desocupado = pd.concat(desocupado, axis=1)
            ocupado = pd.concat(ocupado, axis=1)
            nivel = pd.concat([ocupado, desocupado], axis=1)
            agg_nivel = pd.concat([agg_nivel, nivel], axis=0)

        agg_nivel.sort_index(inplace=True)
        if tipo=='mensual':
            agg_nivel = agg_nivel.groupby(date_set).mean()
        agg_nivel = self.trimestre_movil(agg_nivel)
        agg_nivel['d'] = agg_nivel[['dh15', 'dm15', 'dh25', 'dm25']].sum(axis=1)
        agg_nivel['o'] = agg_nivel[['oh15', 'om15', 'oh25', 'om25']].sum(axis=1)
        # 5. Calcular totales de desocupados y ocupados
        agg_nivel['dh'] = agg_nivel[['dh15', 'dh25']].sum(axis=1)
        agg_nivel['dm'] = agg_nivel[['dm15', 'dm25']].sum(axis=1)
        agg_nivel['oh'] = agg_nivel[['oh15', 'oh25']].sum(axis=1)
        agg_nivel['om'] = agg_nivel[['om15', 'om25']].sum(axis=1)

        # 6. Calcular la fuerza de trabajo por sexo y total
        agg_nivel['fh'] = (agg_nivel['dh'] + agg_nivel['oh'])
        agg_nivel['fm'] = (agg_nivel['dm'] + agg_nivel['om'])
        agg_nivel['ft'] = (agg_nivel['fh'] + agg_nivel['fm'])

        # 7. Calcular las tasas de desocupación por cada trimestre y mes central
        agg_nivel['tdh'] = (agg_nivel['dh'] / agg_nivel['fh']) * 100  # Tasa de desocupados hombres
        agg_nivel['tdm'] = (agg_nivel['dm'] / agg_nivel['fm']) * 100  # Tasa de desocupados mujeres
        agg_nivel['td'] = (agg_nivel['d'] / agg_nivel['ft']) * 100  # Tasa de desocupación total

        agg_nivel = agg_nivel.reset_index().rename(columns=dict(zip(date_set,['ano','mes'])))
        if tipo=='mensual':
            tasa = pd.read_csv(join(self.preprocess_path, self.final_name), sep=';')
            agg_nivel = pd.concat([tasa, agg_nivel], axis=0)
            agg_nivel = agg_nivel.groupby(['ano','mes']).mean().reset_index()
            
        agg_nivel = agg_nivel.round(3)
        agg_nivel.to_csv(join(self.preprocess_path, self.final_name), sep=";", index=False)         

    def nivel_estratificado(self, raw, estado, date_set):
        if 'fact_cal' not in raw.columns:
            raw['fact_cal'] = 1

        estado_mask = raw['cae_especifico'].isin([8, 9]) if estado=='desocupado' else raw['cae_especifico'].isin([1, 2, 3, 4, 5, 6, 7]) if estado=='ocupado' else None
        if estado_mask is None:
            raise ValueError("Valores perimitidos para estado son 'ocupado', 'desocupado'")
        mask_15 = raw['edad'].between(15, 24)
        mask_25 = ~mask_15
        h_mask = raw['sexo'] == 1
        m_mask = raw['sexo'] == 2

        # 3. Desocupados por edad y sexo
        h15 = raw.loc[estado_mask & mask_15 & h_mask,:].groupby(date_set)['fact_cal'].sum().rename(f'{estado[0]}h15')
        m15 = raw.loc[estado_mask & mask_15 & m_mask,:].groupby(date_set)['fact_cal'].sum().rename(f'{estado[0]}m15')
        h25 = raw.loc[estado_mask & mask_25 & h_mask,:].groupby(date_set)['fact_cal'].sum().rename(f'{estado[0]}h25')
        m25 = raw.loc[estado_mask & mask_25 & m_mask,:].groupby(date_set)['fact_cal'].sum().rename(f'{estado[0]}m25')
        return h15, m15, h25, m25 

    def trimestre_movil(self, nivel:pd.DataFrame):
        nivel['dias_mes'] = [monthrange(*index)[-1] for index in nivel.index]
        nivel_pre = nivel.shift(1)
        nivel_pos = nivel.shift(-1)
        dm_pos, dm, dm_pre = nivel_pos['dias_mes'].copy(), nivel['dias_mes'].copy(), nivel_pre['dias_mes'].copy()
        nivel_movil = (nivel_pos.mul(dm_pos, axis=0) + nivel.mul(dm, axis=0) + nivel_pre.mul(dm_pre, axis=0)).div(
            (dm_pos + dm + dm_pre), axis=0) 

        return nivel_movil.drop(columns='dias_mes').dropna(axis=0, how='all')

    def nuevos_datos(self):
        if os.path.isfile(join(self.preprocess_path, self.final_name)):
            tasa = pd.read_csv(join(self.preprocess_path, self.final_name), sep=';')
            ano_mes = tasa.loc[len(tasa)-1, ['ano', 'mes']].astype(int).astype(str).str.cat(sep='-')
            del tasa
            last_date = pd.to_datetime(ano_mes, format='%Y-%m')
        else:
            last_date = pd.Timestamp(year=2010, month=1, day=1)
        trim_movil = {1:'def', 2:'efm', 3:'fma', 4:'mam', 5:'amj', 6:'mjj', 7:'jja', 8:'jas', 9:'aso', 10:'son', 11:'ond', 12:'nde'}

        i = 0
        while True:
            i += 1
            date = last_date + pd.DateOffset(months=i)
            trim = trim_movil[date.month]
            file_name = f"ene-{date.strftime(format='%Y-%m')}-{trim}.csv"
            os.makedirs(join(self.raw_path, 'monthly'), exist_ok=True)
            if not os.path.exists(join(self.raw_path, 'monthly', file_name)):
                request_statement = f'https://www.ine.gob.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/{date.year}/csv/{file_name}'
                response = requests.get(request_statement)
                if response.status_code != 200:
                    logging.warning(f"File download stopped on date {date.year}-{date.month}")
                    break
                else:
                    logging.info(f"Downloading file for date {date.year}-{date.month}")
                response = io.BytesIO(response.content, )
                try:
                    new = pd.read_csv(response, sep=';', encoding='latin1', low_memory=False)
                except pd.errors.ParserError as e:
                    logging.error("Check response content")
                    break
                new.to_csv(join(self.raw_path, 'monthly', file_name), sep=';', index=False)
        

if __name__=='__main__':
    ene = ENE()
    ene.groupby_cae('anual')
    ene.nuevos_datos()
    ene.groupby_cae('mensual')