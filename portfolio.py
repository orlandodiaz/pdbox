"Unfortunate name"

from lib.log import log


class Portfolio(object):

    def __init__(self, tickers, name):
        self.tickers = tickers
        self.name = name

        self.check_if_exists(tickers)

    def blacklist(self, blacklist):
        """This operation is done in-place"""
        for item in blacklist:
            if item in self.tickers:
                self.tickers.remove(item)

    def add(self, ticker):
        """
        Add a specific ticker to your Portfolio
        """
        pass

    def check_if_exists(self, tickers):

        for ticker in tickers[:]:
            path = '/Users/system-void/gdrive/code/data/stocks/5min/%s.txt' % ticker
            try:
                # Get the size (lines) of file (must open file)
                size = sum(1 for l in open(path))
            except Exception as ex:
                log.info('%7s - Ticker not found in equity database. Removing from portfolio' % ticker)
                #print ex
                self.tickers.remove(ticker)