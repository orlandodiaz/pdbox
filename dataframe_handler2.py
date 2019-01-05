import time
from data_handler import make_dataframe_from_csv, correct_csv_df, add_columns
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from portfolio import Portfolio


class DataframeHandler(object):

    def __init__(self, portfolio):

        pass

    def __new__(self, portfolio):
        return self.run_all(portfolio)

    def th_run(self, portfolio):

        pool = ThreadPoolExecutor(len(portfolio.tickers))  # for many urls, this should probably be capped at some value.
        futures = []
        for ticker in portfolio.tickers:
            try:
                data = futures.append([ticker, pool.submit(make_dataframe_from_csv, ticker)])
            except Exception as ex:
                print "Exception ocurred: {0}".format(ex)
                continue

        time.sleep(3)
        return futures

    def mp_worker(self, ticker, data):
        print ticker
        try:
            csv_df = data
            csv_df = correct_csv_df(csv_df)
           # csv_df = add_columns(csv_df)
        except Exception as ex:
            print ex

        else:
            print 'A worker done'
            return csv_df

    def mp_run(self, futures):

        process_pool = ProcessPoolExecutor(7)  # 7 is the most efficient use of cores
        mp_futures = []

        for future in futures:
            try:
                data = future[1].result()
                ticker = future[0]
            except Exception as ex:
                print ex
                continue
            else:
                mp_futures.append([ticker, process_pool.submit(self.mp_worker, ticker, data)])
        time.sleep(5)

        return mp_futures

    def create_stocks(self, mp_futures):
        stocks = []
        for future in mp_futures:
            try:
                stocks.append([future[0], future[1].result()])
            except Exception as ex:
                print ex
                continue

        time.sleep(10)
        return stocks

    def run_all(self, portfolio):
        futures = self.th_run(portfolio)
        mp_futures = self.mp_run(futures)
        stocks = self.create_stocks(mp_futures)
        return stocks


if __name__ == '__main__':
    stock_ticker = ['CLNT']
    my_portfolio = Portfolio(stock_ticker)

    #my_stocks = DataframeHandler(my_portfolio)
    my_stocks = DataframeHandler('hey kids')


    # futures = th_run(my_portfolio)
    # mp_futures = mp_run(futures)


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

