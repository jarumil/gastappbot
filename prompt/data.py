from abc import ABC, abstractmethod
import pandas as pd
import os
import constants.constants as cts
import datetime as dt
import locale

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


class Data(ABC):
    @property
    def data(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.DataFrame
            The complete dataset.
        """
        return self.get_data()
    
    @property
    def filtered_data(self) -> pd.DataFrame:
        """
        Returns
        -------
        pd.DataFrame
            The filtered dataset based on specific criteria.
        """
        return self.get_filtered_data()
    
    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        """
        Abstract method to get the complete dataset.

        Returns
        -------
        pd.DataFrame
            The complete dataset.
        """
        pass

    @abstractmethod
    def get_filtered_data(self) -> pd.DataFrame:
        """
        Abstract method to get the filtered dataset.

        Returns
        -------
        pd.DataFrame
            The filtered dataset.
        """
        pass


class MyData(Data):
    def __init__(self):
        super().__init__()

    def get_data(self) -> pd.DataFrame:
        """
        Reads and processes the data from a CSV file.

        Returns
        -------
        pd.DataFrame
            The processed dataset.
        """
        df = pd.read_csv(os.path.join(cts.DATA_FOLDER, cts.DATA_FILENAME))
        df['Fecha'] = pd.to_datetime(df['Fecha'], origin='1900-01-01', unit='D', errors='coerce')
        df['Mes'] = df['Fecha'].dt.strftime('%B')
        df["MesN"] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        df = df.drop(columns=['Fecha', 'Dividido', 'Total'])
        df.columns = ['Categoria', 'Descripcion', 'Precio', 'Tipo', 'Mes', 'MesN', 'Año']
        df = df.fillna('desconocido')
        df = df.groupby(['Año', 'Mes', 'MesN', 'Categoria', 'Descripcion', 'Tipo'])['Precio'].sum().reset_index()
        df["Año"] = df["Año"].astype(int)
        df["Precio"] = df["Precio"].round(2)
        df = df.sort_values(by=['Año', 'MesN', 'Categoria', 'Descripcion', 'Tipo', 'Precio'], ascending=[False, False, True, True, True, True])
        df = df.drop(columns=['MesN'])

        return df

    def get_filtered_data(self) -> pd.DataFrame:
        """
        Filters the data to include only the last two years.

        Returns
        -------
        pd.DataFrame
            The filtered dataset.
        """
        today = dt.datetime.today()
        # Read the data every time because it might have changed.
        data = self.get_data()

        return data[data['Año'] >= today.year - 2]