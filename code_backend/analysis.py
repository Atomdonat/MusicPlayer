import pandas
import pandas as pd

from shared_config import *


class Analysis:
    def __init__(self, tsv_file_path:str):
        if not os.path.isfile(tsv_file_path):
            raise FileNotFoundError(tsv_file_path)

        self.dataframe = pandas.read_csv(tsv_file_path, sep='\t')
        self.column_names = []
        self._data = []

    def create_new_dataframe(self):
        self.dataframe = pandas.DataFrame(data=self.data, columns=self.column_names)

    @property
    def data(self) -> list:
        return self._data

    @data.setter
    def data(self, new_data: list):
        self._data.append(new_data)

    def check_item_existence(self, column_name: str, value) -> pandas.DataFrame:
        return self.dataframe[self.dataframe[column_name] == value]

    def insert_data_into_dataframe(self, data) -> None:
        tmp_df = pd.DataFrame(data)
        self.dataframe = pd.concat([self.dataframe, tmp_df], axis=1)


# class TrackAnalysis(Analysis):
#     def __init__(self, tsv_file_path: str, track_id: str):
#         super().__init__(tsv_file_path)











