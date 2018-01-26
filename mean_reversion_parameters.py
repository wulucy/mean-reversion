# time period
# Proportion
# proportion of position
# add metrics

import requests
import talib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
import os

os.chdir('/Users/lucy/repos/meanreversion')

print("Running...")

# Get data from Quandl (is there a better API?)
def getDataQuandl(ticker):
    q_data = requests.get("https://www.quandl.com/api/v3/datasets/WIKI/" + ticker + ".csv")
    q_string = StringIO(q_data.text)
    data = pd.read_csv(q_string, sep=",")
    data = data.head(3000) # for time purposes
    data = data.iloc[::-1].reset_index()

    return data

#initial_cash_balance = 10000

# Loop through prices and compare to SMA
def priceLoop(close_prices, dates, initial_cash_balance, timeperiod, prop, proportion_sell, proportion_spent):

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
            new_cash_balance, new_shares = sell(current_close, last_cash_balance, last_shares_held, proportion_sell)
        elif current_close < (1-prop)*current_sma:
            #print("Buying...")
            # BUY
            buy_sell += [1]
            new_cash_balance, new_shares = buy(current_close, last_cash_balance, last_shares_held, proportion_spent)
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

    #calculateMetrics(result)

    return result
    #return buy_sell, close_prices, simp_ma

def buy(current_close, last_cash_balance, last_shares_held, proportion_spent):

    # How much of your cash balance to spend?

    if last_cash_balance > 0.01:\

        spending_cash = last_cash_balance * proportion_spent

        buy_shares = spending_cash/current_close

        # Update info
        new_cash_balance = last_cash_balance - spending_cash
        new_shares = last_shares_held + buy_shares
    else:
        new_cash_balance = last_cash_balance
        new_shares = last_shares_held

    return new_cash_balance, new_shares

def sell(current_close, last_cash_balance, last_shares_held, proportion_sell):

    if last_shares_held > 0:

        selling_shares = last_shares_held * proportion_sell
        sell_debit = current_close*selling_shares

        # Update info
        new_cash_balance = last_cash_balance + sell_debit
        new_shares = last_shares_held - selling_shares
    else:
        new_cash_balance = last_cash_balance
        new_shares = last_shares_held

    return new_cash_balance, new_shares

#def calculateMetrics():
#    pass

# Run everything
def runMeanReversion(unique_id, ticker, initial_cash_balance, timeperiod, prop, proportion_sell, proportion_spent):
    print('Running for', ticker + '...')
    data = getDataQuandl(ticker)
    result = priceLoop(data['Close'].as_matrix(), data['Date'].as_matrix(), initial_cash_balance=initial_cash_balance, timeperiod=timeperiod, prop=prop, proportion_spent=proportion_spent, proportion_sell=proportion_sell)
    result = result[['Date', 'Close', 'SMA', 'Decision', 'Cash Balance', 'Shares Held', 'Total Value']]

    total_return = result.iloc[-1]['Total Value']
    print('Returns for', ticker + ':', str(round((total_return/initial_cash_balance)*100, 2))+'%')
    result.to_csv('result_' + unique_id + '.csv')

    return result, total_return


data = pd.read_csv('AAPL.csv')
data = data.iloc[::-1].reset_index()

try:
    os.mkdir('varying_params_results')
except FileExistsError:
    os.chdir('varying_params_results')

varying_params_df = pd.DataFrame(columns=['Ticker', 'Timeperiod', 'Prop', 'Proportion Sell', 'Proportion Spent', 'Unique ID', 'Initial Cash Balance', 'Total Returns']) # add other metrics

print(data.columns)
initial_cash_balance = 10000
for i in range(2, 7): # 5
    timeperiod = i
    for k in np.arange(0.10, 0.30, 0.05):# 4
        prop = k
        for j in np.arange(0.10, 1.10, 0.30): # 4
            proportion_sell = j
            for l in np.arange(0.10, 1.10, 0.30): # 4 = 320 loops total
                proportion_spent = l
                unique_id = str(timeperiod) + '_' + str(prop) + '_' + str(proportion_sell) + '_' + str(proportion_spent)
                print('Running:', unique_id)
                result = priceLoop(data['Close'].as_matrix(), data['Date'].as_matrix(), initial_cash_balance=initial_cash_balance, timeperiod=timeperiod, prop=prop, proportion_spent=proportion_spent, proportion_sell=proportion_sell)
                total_return = result.iloc[-1]['Total Value']
                percent_return = total_return/initial_cash_balance
                print('Returns:', str(round((total_return/initial_cash_balance)*100, 4))+'%')
                new_df = pd.DataFrame(data={'Ticker': 'AAPL', 'Timeperiod': timeperiod, 'Prop': prop, 'Proportion Sell': proportion_sell, 'Proportion Spent': proportion_spent, 'Unique ID': unique_id, 'Initial Cash Balance': 10000, 'Percent Returns': percent_return}, index=[0])
                varying_params_df = pd.concat([new_df, varying_params_df])
# ADD: generate log file

varying_params_df.to_csv('varying_params_AAPL.csv')

os.chdir('/Users/lucy/repos/meanreversion')
#runMeanReversion('MSFT')
#runMeanReversion('TWTR')
#runMeanReversion('TSCO')
#runMeanReversion('RAD')
