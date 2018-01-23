import requests
import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

print("Running...")

# Get data from Quandl (is there a better API?)
aapl = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/AAPL.csv")
aapl_string = StringIO(aapl.text)
data = pd.read_csv(aapl_string, sep=",")
data = data.head(3000) # for time purposes
data = data.iloc[::-1].reset_index()

# Loop through prices and compare to SMA
def priceLoop(close_prices, dates, initial_cash_balance, timeperiod=30, prop=0.25):

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

    # Initialize data
    buy_sell = [np.nan] * (timeperiod-1)
    cash_balance = [0] * (timeperiod-1)
    first_close = close_prices[0]
    shares_held = [initial_cash_balance/first_close] * (timeperiod-1)
    total_value = [x*y for x, y in zip(shares_held, close_prices[0:29])]

    for i in range(timeperiod-1, len(close_prices)):
        current_close = close_prices[i]
        current_sma = simp_ma[i]
        last_cash_balance = cash_balance[i-1]
        last_shares_held = shares_held[i-1]
        if current_close > (1+prop)*current_sma:
            #print("Selling...")
            # SELL
            buy_sell += [-1]
            new_cash_balance, new_shares = sell(current_close, last_cash_balance, last_shares_held)
        elif current_close < (1-prop)*current_sma:
            #print("Buying...")
            # BUY
            buy_sell += [1]
            new_cash_balance, new_shares = buy(current_close, last_cash_balance, last_shares_held)
        else:
            buy_sell += [0]
            new_cash_balance = last_cash_balance
            new_shares = last_shares_held

        # Update values
        cash_balance += [new_cash_balance]
        shares_held += [new_shares]
        total_value += [new_cash_balance + (new_shares*current_close)]

    # Generate graph of value (w/ color-coded points based on buy/sell??)
    ''' This works but isn't very useful
    plt.plot(range(len(data)), close_prices) #c=buy_sell)
    plt.plot(range(len(data)), simp_ma)
    plt.show()
    '''

    # Store results in dataframe
    result = pd.DataFrame(data={'Date': dates, 'Close': close_prices,
                                'SMA': simp_ma, 'Decision': buy_sell, 'Cash Balance': cash_balance,
                               'Shares Held': shares_held, 'Total Value': total_value})

    return result
    #return buy_sell, close_prices, simp_ma

def buy(current_close, last_cash_balance, last_shares_held):

    if last_cash_balance > 0.01:
        buy_shares = last_cash_balance/current_close

        # Update info
        new_cash_balance = 0
        new_shares = last_shares_held + buy_shares
    else:
        new_cash_balance = last_cash_balance
        new_shares = last_shares_held

    return new_cash_balance, new_shares

def sell(current_close, last_cash_balance, last_shares_held):

    if last_shares_held > 0:
        sell_debit = current_close*last_shares_held

        # Update info
        new_cash_balance = last_cash_balance + sell_debit
        new_shares = 0
    else:
        new_cash_balance = last_cash_balance
        new_shares = last_shares_held

    return new_cash_balance, new_shares


# Save results
result = priceLoop(data['Close'].as_matrix(), data['Date'].as_matrix(), initial_cash_balance=10000, timeperiod=30, prop=0.05)
result = result[['Date', 'Close', 'SMA', 'Decision', 'Cash Balance', 'Shares Held', 'Total Value']]

result.to_csv('result_portfolio.csv')
