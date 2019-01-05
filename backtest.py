import time
import pandas as pd
import datetime
import os
from datetime import datetime as dt
import cPickle as pickle
from log3 import log
from data_handling_utils import add_columns


class Backtest(object):

    stocks_list = None

    def __init__(self, strategy, stock_list, **kwargs):
        """

        Args:
            strategy (Strategy): algorithm trading strategy. Must be of type Strategy
            stock_list: 2d List of stock dataframes
            **kwargs:
        """

        # Initialize class variables
        Backtest.stocks_list = stock_list

        # Save Arguments passed
        self.strategy = strategy
        self.num_of_stocks = len(stock_list)

        # Backtest settings
        self.use_multithreading = False

        # If set to False, Information from pre-market and after-hours wont be used to calculate the indicators.
        # Pros: pre-market/after-market not very liquid and orders don't get filled.
        # Recommendation: Set it to False
        self.extended_hours = True

        # These are the default values for the backtest. It backtests 1 month back by default.
        self.buy_start = '2017-11-01'
        self.buy_end = '2017-12-05'
        self.time_frame = "{0}:{1}".format(self.buy_start,self.buy_end)
        
        # Checkers
        self._is_done = False

        # Backtest results
        self.long_winners = 0
        self.long_losers = 0
        self.short_winners = 0
        self.short_losers = 0
        self.winning_percent = 0

        self.winners = 0
        self.losers = 0

        self.winning_trades = 0
        self.losing_trades = 0
        self.pct_chg_avg = 0
        self.max_win_streak = 0
        self.max_lose_streak = 0

        self.timestamp = str(dt.now())[:16]

        # Optional note to use that will be displayed in the pandas dataframe result dataframe
        if 'note' in kwargs:
            self.note = kwargs['note']
        else:
            self.note = ""

        
        # Other
        self.trade_log = pd.DataFrame(columns=
            ['buy_date', 'ticker', 'buy_price', 'sell_date','sell_price','volume'])


    def disable_extended_hours(self):
        self.extended_hours = False

    def _pass_to_strategy(self, df):
        self.coords = self.strategy.get_buy_coordinates(self, df)
        return self.coords

    def _individual_backtest(self, stock, buy_start, buy_end):

        ticker = stock[0]
        df = stock[1]

        index = 0
        buy_date = 0
        buy_price = 0

        volume = 0
        init = 0

        then = time.time()

        self.buy_start = buy_start
        self.buy_end = buy_end

        proc = os.getpid()

        # print('{0} backtester5:\t {1}\t operated by PID: {2}'.format(str(dt.now().time())[:8], ticker, proc))

        if self.extended_hours is False:
            df = df.ix[df.index.indexer_between_time(datetime.time(9,30), datetime.time(16))]
        else:
            pass

        # Add code to add columns here.
        # df = add_columns(df)

        # Buying range: Date must be the index
        df = df.loc['{buy_start} 9:30'.format(buy_start=self.buy_start):'{buy_end} 16:00'.format(buy_end=self.buy_end)]

        df = df.reset_index()
        df = df.rename({'index': 'date'}, axis='columns')

        index_array = self.strategy.get_buy_coordinates(df)

        log.debug('Index array is %s' % index_array)

        # self.strategy.check_for_conditions(self, df, ticker, index_array)

        trade_row = pd.DataFrame(columns=
                                 ['index', 'buy_date','ticker','buy_price', 'sell_date','sell_price', 'volume'])
        for index in index_array:
            # Store the close as the buying price
            buy_price = df.iloc[index]['close']
            buy_date = df.iloc[index]['date']

            init = int(index) # Initial value
            volume = df.iloc[index]['volume']

            sell_date, sell_price = self.strategy.sell_algorithm(init, ticker, df)

            sell_date = sell_date
            sell_price = sell_price

            # print "inside loop %.4f" % sell_date
            # print "inside loop %.4f" % sell_price

            log.info('%7s - Bought @ %.3f at LOC: %d ' % (ticker, buy_price, index))

           # print "%s backtester2: \t %s \t BUY  @ %.3f\t LOC: %d" % \
           #       (dt.now().strftime("%H:%M:%S"), ticker, buy_price, index)

            if sell_date or sell_price != 0:
                trade_row.loc[trade_row.__len__()]=[index, buy_date, ticker, buy_price, sell_date, sell_price, volume]

        if len(index_array) == 0:
            current2_time = str(dt.now().time())[:8]

            log.info('%7s - Operation by PID %s. Task completed in %s' % (ticker, proc, time.time() - then))


            # print('{0}\t Ticker {1} being operated on by process id: {2}'.format(current2_time, ticker, proc)),
            # print "%s backtester2: \t %s \t Task completed in:  %s" \
            #      % (dt.now().strftime("%H:%M:%S"), ticker, time.time() - then)

        else:

            log.info('%7s - Operation by PID %s. Task completed in %s' % (ticker, proc, time.time() - then))

            # print "%s backtester2: \t %s \t Task completed in:  %s" \
            #      % (dt.now().strftime("%H:%M:%S"), ticker, time.time() - then)

            # print "Test %d" % sell_date
            # print "test %d" % sell_price
            # if sell_date or sell_price != 0:
            self.trade_log = self.trade_log.append(trade_row)

            self._isdone = True

    def _start_loop(self, buy_start, buy_end):
        for i in Backtest.stocks_list:
            self._individual_backtest(i, buy_start, buy_end)

    def run(self, buy_start, buy_end):
        self.buy_start = buy_start
        self.buy_end = buy_end
        self._start_loop(buy_start, buy_end)
        self.save_results()

    def save_results(self):

        self.trade_log['diff'] = self.trade_log['sell_price'] - self.trade_log['buy_price']
        self.trade_log['pct_change'] = (self.trade_log['diff'] / self.trade_log['buy_price']) * 100
        self.trade_log = self.trade_log.sort_values('buy_date')

        if self.strategy.direction == "short":
            self.winners =  len(self.trade_log[(self.trade_log['pct_change'] < 0)])
            self.losers = len(self.trade_log[(self.trade_log['pct_change'] > 0)])
        elif self.strategy.direction == "long":
            self.winners = len(self.trade_log[(self.trade_log['pct_change'] > 0)])
            self.losers = len(self.trade_log[(self.trade_log['pct_change'] < 0)])
        else:
            raise ValueError('Invalid position type. Strategy position type must be "short" or "long"')

     #   self.short_losers = len(self.trade_log[(self.trade_log['pct_change'] > 0)])

        self.pct_chg_avg = self.trade_log['pct_change'].mean()


        if self.winners and self.losers != 0:
            self.winning_percent = (float(self.winners) / (self.losers + self.winners) * 100)
        else:
            self.winning_percent = 0

    def pickle_results(self):
        pickle_name = self.strategy.name
        pickle_name = pickle_name.lower().replace(' ', '_')
        f = open("bt_results/{0}-{1}".format(self.timestamp.replace(' ', '-'), pickle_name), "wb")

        log.info("Pickling backtesting object")
        pickle.dump(self, f)
        f.close()

    def print_results(self):
        print
        print 'strategy: {0}\t Time: {1}\t Stocks: {2}'.format(self.strategy.name, self.time_frame, self.num_of_stocks)
        print '-------------------------------------------------------------------------------------------------------'

        print self.trade_log

        print

        print 'Winning trades: {0}'.format(self.winners)
        print 'Losing trades: ', self.losers
#        print 'Winning percent', self.winners / (self.losers + self.winners)

       #  print 'Long trategy:'
       #  print '-------------'
       #  print 'Winning trades: {0}'.format(self.long_winners)
       #  print 'Losing trades: ', self.long_losers
       # # print 'Winning percent', self.long_winners / (self.long_losers + self.long_winners)
       #  print
       #
       #  print 'Short Strategy'
       #  print '--------------'
       #  print 'Winning trades: ', self.short_winners
       #  print 'Losing trades: ', self.short_losers
       #  print "Winning percent: %.1f %%" % self.winning_percent

        print 'pct_change avg: ', self.pct_chg_avg

        print '4_mo_high window'
        print 'Best month'
        print 'Longest win streak'
        print 'Longest lose streak'
        print 'Month totals'