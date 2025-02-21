from abc import ABC, abstractmethod
import pandas as pd
import os
import constants.constants as cts
import datetime as dt
import locale

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


class Data(ABC):
    @abstractmethod
    def data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def filtered_data(self) -> pd.DataFrame:
        pass


class MyData(Data):
    def __init__(self):
        super().__init__()

    def data(self) -> pd.DataFrame:
        df = pd.read_csv(os.path.join(cts.DATA_FOLDER, cts.DATA_FILENAME))
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
        df['Mes'] = df['Fecha'].dt.strftime('%B')
        df["MesN"] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        df = df.drop(columns=['Fecha', 'Dividido', 'Total'])
        df.columns = ['Categoria', 'Descripcion', 'Precio', 'Tipo', 'Mes', 'MesN', 'Año']
        df["Precio"] = df["Precio"].str.replace('.', '').str.replace(',', '.').astype(float)
        df = df.fillna('desconocido')
        df = df.groupby(['Año', 'Mes', 'MesN', 'Categoria', 'Descripcion', 'Tipo'])['Precio'].sum().reset_index()
        df = df.sort_values(by=['Año', 'MesN', 'Categoria', 'Descripcion', 'Tipo', 'Precio'])
        df = df.drop(columns=['MesN'])
        df["Precio"] = df["Precio"].round(2)

        return df

    def filtered_data(self) -> pd.DataFrame:
        today = dt.datetime.today()
        # Read the data every time because it might have changed.
        data = self.data()

        return data[data['Año'] >= today.year - 2]