import pandas as pd

filename = 'crawling/board_data.csv'
data = pd.read_csv(filename, index_col='code').T
data = data.where(pd.notnull(data), None).to_dict()