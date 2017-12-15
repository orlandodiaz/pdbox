from backtest import Backtest
from portfolio import Portfolio
from strategies.sma_crossover import SMACrossOver
from strategies.strat_overbought import OverboughtMorning
from strategies.strat_oversold import OversoldMorning
from strategies.buy_randomly import BuyRandomly
import cPickle as pickle
from backtest_history import get_backtests
from dataframe_handler import build_dataframes
from modules.intrinio import Intrinio
from strategies.strat_adx import ADXStrat

if __name__ == '__main__':

    # tickers = ['DPW', 'GROW', 'SGRP', 'CBIO', 'GBR', 'MOSY', 'CREG', 'ONCS','EVEP', 'ISIG', 'CALI']

    #tickers = ['GBR']
    #tickers = ['SRAX','KOOL','DYSL']
    #tickers = ['AAPL, MSFT, TWTR']
    # tickers =  ['ONP', 'CNET', 'RCON', 'CREG']
    # tickers = ['ONP', 'CNET', 'RCON', 'CREG', 'AMMA', 'SRAX', 'DYSL', 'OPTT', 'KOOL', 'ONTX', 'CLNT', 'CMLS', 'APHB', 'ISIG',
    #        'CBIO', 'STAF', 'SSI', 'ONCS', 'QRHC', 'SKLN', 'CNIT', 'BONT', 'EVEP', 'MLSS', 'ENRJ', 'LIQT', 'MOSY', 'SMIT',
    #        'CRTN', 'ITEK', 'ARGS', 'LTRX', 'MICT', 'IGC', 'NEOT', 'SSKN', 'ABIO', 'OPGN', 'USEG', 'TST', 'NURO', 'TTNP',
    #        'DRIO', 'PZRX', 'AKER', 'YECO']
    #intrinio = Intrinio()
    #tickers = intrinio.get_stocks()

    tickers = pickle.load(open("pickles/stocks_less_than_500m.p", "rb"))
    #tickers = tickers[:400]

    # Create portfolio
    my_portfolio = Portfolio(tickers, "Normal < 200m")

    # Blacklist certain stocks
    my_portfolio.blacklist(['BURG', 'CVM.W', 'AGM.A'])

    # Create dataframes from portfolio. Uses threads and multiprocessing
    stocks = build_dataframes(my_portfolio)  # => weird multidimensional list of stocks

    # Load strategies
    # strategy = OverboughtMorning('Overbought Morning')
    # strategy = ADXStrat('STRAT ADX')
    strategy = OversoldMorning('Oversold morning')
    # sma_crossover = SMACrossOver('SMA 100 crossing over SMA 400')
    # buy_randomly = BuyRandomly('Buys random stocks and sells at random times')

    # Backtest it against our historical time-series stock dataframes. Add optional note
    backtest = Backtest(strategy, stocks, note="defaults")
    backtest.extended_hours = True
    backtest.run('2017-07-01', '2017-12-05')

    # Print backtest results
    backtest.print_results()

    # Save it. If you like it
    backtest.pickle_results()

    # See Backtest history
    backtest_history = get_backtests()
