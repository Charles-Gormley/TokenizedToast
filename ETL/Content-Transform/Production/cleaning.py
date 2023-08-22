import json
from datetime import datetime, timedelta

class Cleaner:
    def __init__(self, json_file_path:str):
        with open(json_file_path, 'r') as f:
            self.data = json.load(f)

    def flatten_initial_dataframe(self):
        flattened_data = []
        for sublist in self.data:
            if isinstance(sublist, list):
                for item in sublist:
                    if isinstance(item, list):
                        for subitem in item:
                            if isinstance(subitem, dict):
                                flattened_data.append(subitem)
                    elif isinstance(item, dict):
                        flattened_data.append(item)
            elif isinstance(sublist, dict):
                flattened_data.append(sublist)
        self.data = flattened_data


    def remove_undated_articles(self):
        self.data = [item for item in self.data if isinstance(item, dict) and item.get('date') != 'None']


    def remove_older_articles(self, date_column:str):
        # get date three days ago
        three_days_ago = datetime.now() - timedelta(days=3)

        cleaned_data = []
        for item in self.data:
            # check if the item is a dictionary and contains the 'date' key
            if isinstance(item, dict) and date_column in item:
                # convert date_column to datetime if it isn't already
                item_date = datetime.strptime(item[date_column], "%Y-%m-%d") # Assuming the date is in 'YYYY-MM-DD' format

                # select only rows where date_column is later than three days ago
                if item_date > three_days_ago:
                    cleaned_data.append(item)
                    
        self.data = cleaned_data


    def remove_empty_articles(self):
        pass

    def clean_data(self) -> list:
        '''Main Function'''
        self.flatten_initial_dataframe()
        self.remove_undated_articles()
        self.remove_older_articles('date') # Assuming 'date' is the key for dates in your dictionaries
        
        return self.data
