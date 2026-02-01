import catboost as cb
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
import matplotlib as plt

from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.metrics import mean_squared_error

df = pd.read_csv("dataset.csv") ## wait until available

X = df.drop(columns=["price"])
y = df["price"]

categorical_features = [
    "postcode",
    "property_type"
]
