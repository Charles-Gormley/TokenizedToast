from cleaning import Cleaner
import pickle

content_json_path = 'C:/Users/Charl/Documents/Projects/TokenizedToast/ETL/RSS-Extractor/content/json'
cleaner = Cleaner()
df = cleaner.clean_dataframe()

df.to_pickle('cleaned-dataframe.pkl')