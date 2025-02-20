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
        df['Año'] = df['Fecha'].dt.year
        df = df.drop(columns=['Fecha', 'Dividido', 'Total'])
        df.columns = ['Categoria', 'Descripcion', 'Precio', 'Tipo', 'Mes', 'Año']
        df["Precio"] = df["Precio"].str.replace('.', '').str.replace(',', '.').astype(float)
        df["Precio"] = df["Precio"].round(2)
        df = df.fillna('')
        df = df.groupby(['Año', 'Mes', 'Categoria', 'Descripcion', 'Tipo'])['Precio'].sum().reset_index()

        return df

    def filtered_data(self) -> pd.DataFrame:
        today = dt.datetime.today()
        # Read the data every time because it might have changed.
        data = self.data()

        return data[data['Año'] >= today.year - 2]