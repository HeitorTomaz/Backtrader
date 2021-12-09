from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import os.path
from time import sleep
from alpha_vantage.cryptocurrencies import CryptoCurrencies

class Alpha_Vantage_Get_Data():
    def __init__(self, token = 'JUW3PS6IEEDT649G', data_dir = './Data/', debug = False):
        self.TOKEN = token
        self.DATA_DIR = data_dir
        self.DEBUG = debug
        pass

    def __alpha_vantage_eod(self, symbol, compact=False, *args, **kwargs):
        size = 'compact' if compact else 'full'

        if self.DEBUG:
            print('Downloading: {}, Size: {}'.format(symbol, size))

        #if symbol not in ('BTC'):
        alpha_ts = TimeSeries(key=self.TOKEN, output_format='pandas')
        data, meta_data = alpha_ts.get_daily(symbol=symbol, outputsize=size)
        # else:
        #     print("Call crypto api")
        #     alpha_cc = CryptoCurrencies(key=self.TOKEN, output_format='pandas')
        #     data, meta_data = alpha_cc.get_digital_currency_daily(symbol='BTC', market='CNY', outputsize=size)

        print("20 sec delay begin")
        sleep(20)
        print("20 sec delay end")
        
        #Convert the index to datetime.
        data.index = pd.to_datetime(data.index)
        data.columns = ['open', 'high', 'low', 'close','volume']
        data = data.iloc[::-1]
        data.to_csv(self.DATA_DIR + symbol + ".csv")

        # if self.DEBUG:
        #     print(data)
        return data

    def __file_exists(self, symbol):
        return os.path.isfile(self.DATA_DIR + symbol + ".csv")

    def __get_alpha_vantage_csv (self, symbol):
        if self.DEBUG:
            print('Get CSV Data of: {}'.format(symbol))
        data = pd.read_csv (self.DATA_DIR + symbol + ".csv", index_col=0)
        data.index = pd.to_datetime(data.index)
        return data
        
    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)
    
    def get_stock_data(self, symbol_list):
        data_list = list()
        for symbol in symbol_list:
            try:
                data = pd.DataFrame()
                sb = symbol + (".SAO" if self.hasNumbers(symbol) else "")
                if self.__file_exists(sb):
                    data = self.__get_alpha_vantage_csv(sb)
                else:
                    data = self.__alpha_vantage_eod(sb)
                data_list.append((data, symbol))
            except:
                print("Error getting data for: {}".format(symbol))

        return data_list


