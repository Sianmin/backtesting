from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from binance.client import Client
from binance.enums import *
import config
import pandas as pd
from backtesting.test import SMA
from datetime import datetime, timedelta, date


client = Client(config.API_KEY, config.API_SECRET)
            

def print_file(pair, interval, name, initial_date, final_date):

    # request historical candle (or klines) data
    bars = client.get_historical_klines(pair, interval, initial_date, final_date)
    
    # delete unwanted data - just keep date, open, high, low, close
    for line in bars:
        del line[6:]
    
    # save as CSV file 
    df = pd.DataFrame(bars, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    #df.set_index('Date', inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], unit='ms', origin='unix')
    df.to_csv(name)   
    

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10*24)
        self.ma2 = self.I(SMA, price, 20*24)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell() 


if __name__ == "__main__":
    interested_day = 365*4
    today = datetime.now().strftime("%d %b, %Y")
    dateTimeObj2 = date.today() - timedelta(days=interested_day)
    initial_day = dateTimeObj2.strftime("%d %b, %Y")

    # Print file
    filename = "BTC_1h.csv"
    print_file('BTCUSDT', '1h', filename, initial_day, today)

    # Read file
    prices = pd.read_csv(filename, index_col='Date', parse_dates=True)

    # Backtest
    backtest = Backtest(prices, SmaCross,
                cash=100000, commission=.001,
                exclusive_orders=True)
    output = backtest.run()
    print(filename)
    print(output)
    backtest.plot()
