import pandas as pd
import datetime as dt
import constants.constants as cts
import os

class Prompt:
    def __init__(self):
        self._data = None
        self.prompt = None

    def generate_prompt(self, years: int = 2) -> None:
        self.prompt = cts.PROMPT.format(data_str=self._filter_data(years).to_string(index=False))

    def _read_data(self) -> None:
        df = pd.read_csv(os.path.join(cts.DATA_FOLDER, cts.DATA_FILENAME))
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
        df['Mes'] = df['Fecha'].dt.month
        df['Año'] = df['Fecha'].dt.year
        df = df.drop(columns=['Fecha', 'Dividido', 'Total'])
        df.columns = ['Categoria', 'Descripcion', 'Precio', 'Tipo', 'Mes', 'Año']
        df["Precio"] = df["Precio"].str.replace('.', '').str.replace(',', '.').astype(float)
        df["Precio"] = df["Precio"].round(2)
        df = df.fillna('')
        df = df.groupby(['Año', 'Mes', 'Categoria', 'Descripcion', 'Tipo'])['Precio'].sum().reset_index()

        self._data = df
    
    def _filter_data(self, years: int = 2) -> pd.DataFrame:
        if self._data is None:
            self._read_data()

        today = dt.datetime.today()
        df_filtered = self._data[self._data['Año'] >= today.year - years]
        
        return df_filtered
