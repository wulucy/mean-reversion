# create virtualenv with python 3.4 to run
import requests
import talib

data = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/AAPL.csv")
