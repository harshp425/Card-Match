import pandas as pd

data = pd.read_json("backend/dataset/dataset.json")
print(len(data))