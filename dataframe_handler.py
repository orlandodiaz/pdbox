import time
from data_handler import read_csv_df, correct_csv_df, add_columns
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from portfolio import Portfolio
import datetime
from lib.log import log
import pickle

def th_run(my_portfolio):

    pool = ThreadPoolExecutor(len(my_portfolio.tickers))  # for many urls, this should probably be capped at some value.
    futures = []
    for ticker in my_portfolio.tickers:
        try:
            data = futures.append([ticker, pool.submit(read_csv_df, ticker)])
        except Exception as ex:
            print "Exception ocurred: {0}".format(ex)
            continue

    time.sleep(3)

    return futures


def mp_worker(ticker, data):
    try:
        csv_df = data
        csv_df = correct_csv_df(csv_df)
        csv_df =  csv_df.ix[csv_df.index.indexer_between_time(datetime.time(9,30), datetime.time(16))]
        csv_df = add_columns(csv_df)
    except Exception as ex:
        print ex

    else:
        log.info('%7s - Worker has corrected CSV file and added the appropriate columns' % ticker)
        return csv_df


def mp_run(futures):

    process_pool = ProcessPoolExecutor(7)  # for many urls, this should probably be capped at some value.
    mp_futures = []

    for future in futures:

        try:
            data = future[1].result()
            ticker = future[0]
        except Exception as ex:
            print ex
            continue
        else:
            mp_futures.append([ticker, process_pool.submit(mp_worker, ticker, data)])

    time.sleep(5)

    return mp_futures

def create_stocks(mp_futures):

    stocks = []

    for future in mp_futures:
        try:
            stocks.append([future[0], future[1].result()])
        except Exception as ex:
            print ex
            continue

    time.sleep(10)
    return stocks


def build_dataframes(my_portfolio):
    print "Loading stocks into memory"
    futures = th_run(my_portfolio)
    mp_futures = mp_run(futures)
    stocks = create_stocks(mp_futures)
    return stocks


if __name__ == '__main__':
    ticker = ['CLNT']
    my_portfolio = Portfolio(ticker, "test")
    futures = th_run(my_portfolio)
    mp_futures = mp_run(futures)

    log.debug('Pickling stock list')
    #pickle.dump(mp_futures, open('pickles/stock_list', 'wb'))


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

