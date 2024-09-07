import pandas
import pandas as pd

from shared_config import *


# Idea:
#   - create PCA, tSNE and UMAP scatter-plots for data
#   - create neural Network for Tracks
#   -
#   -
#   -
#   -


class TrackAnalysis:
    def __init__(self, tsv_file_path: str):
        if not os.path.isfile(tsv_file_path):
            raise FileNotFoundError(tsv_file_path)

        self.dataframe = pandas.read_csv(tsv_file_path, sep='|')
        self.file_path = tsv_file_path
        self.columns = list(self.dataframe.columns)
        self.data = []

    def add_data_row(self, new_rows: list[dict]) -> None:
        new_dataframe = pd.DataFrame(new_rows)
        updated_dataframe = pd.concat([self.dataframe, new_dataframe], ignore_index=True)
        updated_dataframe.to_csv(path_or_buf=self.file_path, sep='|')

    def remove_data_row(self, id_column: str, value) -> None:
        if not self.check_column_existence(id_column):
            raise KeyError("{} does not exist. Valid Column names are:\n{}".format(id_column, self.columns))
        if self.check_item_existence(id_column, value):
            self.dataframe = self.dataframe[self.dataframe[id_column] != value]

    def check_item_existence(self, column_name: str, value) -> bool:
        if not self.check_column_existence(column_name):
            raise KeyError("{} does not exist. Valid Column names are:\n{}".format(column_name, self.columns))
        return value in self.dataframe[column_name].values

    def check_column_existence(self, column_name: str) -> bool:
        return column_name in self.columns

    def append_new_track_to_data(
        self,
        track_id: str,
        track_acousticness: float,
        track_danceability: float,
        track_duration_ms: int,
        track_energy: float,
        track_instrumentalness: float,
        track_key: int,
        track_liveness: float,
        track_loudness: float,
        track_mode: int,
        track_speechiness: float,
        track_tempo: float,
        track_valence: float,
    ):
        new_track = {
            'track_id': track_id,
            'track_acousticness': track_acousticness,
            'track_danceability': track_danceability,
            'track_duration_ms': track_duration_ms,
            'track_energy': track_energy,
            'track_instrumentalness': track_instrumentalness,
            'track_key': track_key,
            'track_liveness': track_liveness,
            'track_loudness': track_loudness,
            'track_mode': track_mode,
            'track_speechiness': track_speechiness,
            'track_tempo': track_tempo,
            'track_valence': track_valence
        }
        self.data.append(new_track)

    def add_data_rows(self) -> None:
        self.add_data_row(self.data)

    def get_track_analysis(self, track_id: str) -> dict | None:
        if self.check_item_existence(column_name='track_id', value=track_id):
            track_data = self.dataframe.loc[self.dataframe['track_id'] == track_id]

            # Create a new dictionary with the extracted data
            new_track = {col: track_data[col].iloc[0] if not pd.isna(track_data[col].iloc[0]) else None
                         for col in self.columns}

            return new_track
        return None


if __name__ == '__main__':
    track = TrackAnalysis(tsv_file_path=track_analysis_tsv_file_path)
