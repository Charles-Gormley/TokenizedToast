import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class Cleaner:
    def __init__(self, json_file_path:str):
        self.df = pd.read_json(json_file_path)
        
    def flatten_initial_dataframe(self):
        array_of_dicts = np.concatenate(np.concatenate(self.df.values))
        self.df = pd.DataFrame(list(array_of_dicts))
        
    def remove_undated_articles(self):
        self.df = self.df[self.df.date != "None"]

    def remove_older_articles(self, date_column:str):
        # convert date_column to datetime if it isn't already
        self.df[date_column] = pd.to_datetime(self.df[date_column])

        # get date three days ago
        three_days_ago = datetime.now() - timedelta(days=3)

        # select only rows where date_column is later than three days ago
        self.df = self.df.loc[self.df[date_column] > three_days_ago]

    def remove_empty_articles(self):
        pass

    def clean_dataframe(self) -> pd.DataFrame:
        '''Main Function'''
        self.flatten_initial_dataframe()
        self.remove_undated_articles()
        self.remove_older_articles()
        
        return self.df
