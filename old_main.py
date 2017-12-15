from data_handler import read_csv_df, correct_csv_df, add_columns
from backtest import Backtest
from portfolio import Portfolio
from strategies.sma_crossover import SMACrossOver
from strategies.strat_overbought import OverboughtMorning
import cPickle as pickle
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from backtest_history import get_backtests
import dataframe_handler
import time

if __name__ == '__main__':

    #tickers = ['SRAX','KOOL','DYSL']
    # tickers =  ['ONP', 'CNET', 'RCON', 'CREG']
    # tickers = ['ONP', 'CNET', 'RCON', 'CREG', 'AMMA', 'SRAX', 'DYSL', 'OPTT', 'KOOL', 'ONTX', 'CLNT', 'CMLS', 'APHB', 'ISIG',
    #        'CBIO', 'STAF', 'SSI', 'ONCS', 'QRHC', 'SKLN', 'CNIT', 'BONT', 'EVEP', 'MLSS', 'ENRJ', 'LIQT', 'MOSY', 'SMIT',
    #        'CRTN', 'ITEK', 'ARGS', 'LTRX', 'MICT', 'IGC', 'NEOT', 'SSKN', 'ABIO', 'OPGN', 'USEG', 'TST', 'NURO', 'TTNP',
    #        'DRIO', 'PZRX', 'AKER', 'YECO']
    tickers = pickle.load(open("stocks_less_than_200m.p", "rb"))
    #tickers = tickers[:400]

    #tickers = ['CLNT']

    # Create portfolio
    my_portfolio = Portfolio(tickers)

    # Blacklist certain stocks
    my_portfolio.blacklist_in_place(['BURG', 'CVM.W', 'AGM.A'])

    pool = ThreadPoolExecutor(len(my_portfolio.tickers))  # for many urls, this should probably be capped at some value.
    futures = []
    for ticker in my_portfolio.tickers:
        try:
            data = futures.append([ticker, pool.submit(read_csv_df, ticker)])
        except Exception as ex:
            print ex
            continue

    time.sleep(3)

    def worker(ticker, data):
        print ticker
        try:
            csv_df = data
            csv_df = correct_csv_df(csv_df)
            csv_df = add_columns(csv_df)
        except Exception as ex:
            print ex

        else:
            print 'A worker done'
            return csv_df

    process_pool = ProcessPoolExecutor(7)  # for many urls, this should probably be capped at some value.
    p_futures = []

    for future in futures:

        try:
            data = future[1].result()
            ticker = future[0]
        except Exception as ex:
            print ex
            continue
        else:
            p_futures.append([ticker, process_pool.submit(worker, ticker, data)])

    time.sleep(5)

    print p_futures
    stocks = []
    for future in p_futures:
        try:
            stocks.append([future[0], future[1].result()])
        except Exception as ex:
            print ex
            continue

    # stocks = []
    # for ticker in my_portfolio.tickers:
    #     try:
    #         csv_df = read_csv_df(ticker)
    #     except Exception as ex:
    #         print ex
    #         print 'Skipping stock'
    #         continue
    #     else:
    #         csv_df = correct_csv_df(csv_df)
    #         csv_df = add_columns(csv_df)
    #         stocks.append([ticker, csv_df])

    # Load strategies
    overbought_morning = OverboughtMorning('Overbought Morning Strategy')
    # sma_crossover = SMACrossOver('SMA 100 crossing over SMA 400')

    # Backtest it against time-series stock dataframes
    backtester_ob = Backtest(overbought_morning, stocks)
    backtester_ob.run('2016-02-01', '2017-12-01')

    # backtest1 = Backtest(overbought_morning, stocks)
    #backtest1.run('2010-08-01', '2017-11-08')

    # See Backtest results
    backtester_ob.print_results()

    # Save it. If you like it
    backtester_ob.pickle_results()

    # See Backtest history
    backtest_history = get_backtests()



    # print backtest1.winning_percent

    # print backtest2.winning_percent

    #print backtest1.print_results()
    # print backtest2.print_results()
