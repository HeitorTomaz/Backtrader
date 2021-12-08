import backtrader as bt
from datetime import datetime
import sys
sys.path.insert(1, 'D:\Sistemas\Backtrader\GetData\GetData')
from Alpha_Vantage_Get_Data import Alpha_Vantage_Get_Data as avgd
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)

class maCross(bt.Strategy):
    '''
    For an official backtrader blog on this topic please take a look at:

    https://www.backtrader.com/blog/posts/2017-04-09-multi-example/multi-example.html

    oneplot = Force all datas to plot on the same master.
    '''
    params = dict(
        sma1=5,
        sma2=15,
        printout=False,
        oneplot=True
    )
    # (
    # ('sma1', 5),
    # ('sma2', 15),
    # ('oneplot', True)
    # )


    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        '''
        Create an dictionary of indicators so that we can dynamically add the
        indicators to the strategy using a loop. This mean the strategy will
        work with any numner of data feeds. 
        '''
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            self.inds[d]['sma1'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma1)
            self.inds[d]['sma2'] = bt.indicators.SimpleMovingAverage(
                d.close, period=self.params.sma2)
            self.inds[d]['cross'] = bt.indicators.CrossOver(self.inds[d]['sma1'],self.inds[d]['sma2'])

            if i > 0: #Check we are not on the first loop of data feed:
                if self.p.oneplot == True:
                    d.plotinfo.plotmaster = self.datas[0]

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name
            pos = self.getposition(d).size
            cash = self.getposition().size
            #if not pos:  # no market / no orders
            if self.inds[d]['cross'][0] == 1:
                self.order_target_percent(data=d, target=0.4)
            elif self.inds[d]['cross'][0] == -1:
                self.order_target_percent(data=d, target=-0)
            # else:
            #     if self.inds[d]['cross'][0] == -1:
            #         self.close(data=d)
            #         self.buy(data=d, size=1000)
            #     elif self.inds[d]['cross'][0] == 1:
            #         self.close(data=d)
            #         self.sell(data=d, size=1000)

    def notify_trade(self, trade):
        dt = self.data.datetime.date()
        if trade.isopen:
            self.log('{} {} Open: Size {}, Price {}'.format(
                                                dt,
                                                trade.data._name,
                                                trade.size, 
                                                round(trade.price ,2)))
        elif trade.isclosed:
            self.log('{} {} Closed: PnL Gross {}, Net {} '.format(
                                                dt,
                                                trade.data._name,
                                                round(trade.pnl,2),
                                                round(trade.pnlcomm,2)))



class PandasData_custom(bt.feeds.PandasData):
    params = (('open', 0),
        ('high', 1),
        ('low', 2),
        ('close', 3),
        ('volume', 4),     
    )

#Variable for our starting cash
startcash = 10000

#Create an instance of cerebro
cerebro = bt.Cerebro()

#Add our strategy
cerebro.addstrategy(maCross, oneplot=False)

#Get Data
symbol_list = ['BOVA11','SMAL11']
av = avgd(debug = True, data_dir = './GetData/Data/')
print(av.DATA_DIR)
data_list = av.get_stock_data(
                symbol_list)
del av
#print (data_list)
for i in range(len(data_list)):    

    data = PandasData_custom(
                dataname=data_list[i][0], # This is the Pandas DataFrame
                name=data_list[i][1], # This is the symbol
                timeframe=bt.TimeFrame.Days,
                compression=1,
                fromdate=datetime(2016,1,1),
                todate=datetime(2021,1,1)
                )

    #Add the data to Cerebro
    cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(startcash)

#set sharpe
cerebro.addanalyzer(SharpeRatio, timeframe=bt.TimeFrame.Days, compression=3, factor=252,annualize =True, riskfreerate=0.06)
cerebro.addanalyzer(AnnualReturn)
# cerebro.addanalyzer(SharpeRatio, timeframe=bt.TimeFrame.Days, compression=3, factor=252,annualize =True)
cerebro.addanalyzer(TradeAnalyzer)

cerebro.addwriter(bt.WriterFile, rounding=4)

# Run over everything
results = cerebro.run()

#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

#Print out the final result
print('Final Portfolio Value: ${}'.format(portvalue))
print('Sharpe Ratio: ', results[0].analyzers.sharperatio.get_analysis()['sharperatio'])
# print('SQN: ', results[0].analyzers.SQN.get_analysis()['SQN'])
print('P/L: ${}'.format(pnl))

#Finally plot the end results
cerebro.plot(style='candlestick')


# #Print out the final result
# print('Final Portfolio Value: ${}'.format(portvalue))
# print('P/L: ${}'.format(pnl))

# #Finally plot the end results
# cerebro.plot(style='candlestick')