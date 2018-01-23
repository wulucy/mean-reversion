# create virtualenv with python 3.4 to run
import requests
import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# Get data from Quandl (is there a better API?)
aapl = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/AAPL.csv")
aapl_string = StringIO(aapl.text)
data = pd.read_csv(aapl_string, sep=",")
data = data.head(3000) # for time purposes

# Loop through prices and compare to SMA
def priceLoop(close_prices, dates, timeperiod=30, prop=0.25):

    '''
    Parameters
    --------
    close_prices : array
        Closing prices.
    dates : array
        Corresponding dates.
    timeperiod : int, default 30
        Previous days over which SMA
        is calculated.
    prop : int, default 0.25
        Proportion under/over SMA that
        triggers buy/sell signal.
    '''

    simp_ma = talib.SMA(close_prices, timeperiod=timeperiod)

    buy_sell = [np.nan]*(timperiod-1)

    for i in range(timeperiod-1, len(close_prices)):
        current_close = close_prices[i]
        current_sma = simp_ma[i]
        if current_close > (1+prop)*current_sma:
            # SELL
            buy_sell += [-1]
        elif current_close < (1-prop)*current_sma:
            # BUY
            buy_sell += [1]
        else:
            # DO NOTHING
            buy_sell += [0]

    # Generate graph of value (w/ color-coded points based on buy/sell??)
    ''' This works but isn't very useful
    plt.plot(range(len(data)), close_prices) #c=buy_sell)
    plt.plot(range(len(data)), simp_ma)
    plt.show()
    '''

    # Store results in dataframe
    result = pd.DataFrame(data={'Date': dates, 'Close': close_prices,
    'SMA': simp_ma, 'Decision': buy_sell})

    return result
    #return buy_sell, close_prices, simp_ma

result = priceLoop(data['Close'].as_matrix(), data['Date'].as_matrix(), timeperiod=30)
result = result[['Date', 'Close', 'SMA', 'Decision']]

result.to_csv('result.csv')
