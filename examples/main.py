from backtest.backtest import Backtest
from backtest.universe import Universe
from strategies.strat_oversold import OversoldMorning
from backtest.backtest_history import get_backtests
from backtest.dataframe_handler import build_dataframes

if __name__ == '__main__':

    tickers = [
        'ONP', 'CNET', 'RCON', 'CREG', 'AMMA', 'SRAX', 'DYSL', 'OPTT', 'KOOL',
        'ONTX', 'CLNT', 'CMLS', 'APHB', 'ISIG', 'CBIO', 'STAF', 'SSI', 'ONCS',
        'QRHC', 'SKLN', 'CNIT', 'BONT', 'EVEP', 'MLSS', 'ENRJ', 'LIQT', 'MOSY',
        'SMIT', 'CRTN', 'ITEK', 'ARGS', 'LTRX', 'MICT', 'IGC', 'NEOT', 'SSKN',
        'ABIO', 'OPGN', 'USEG', 'TST', 'NURO', 'TTNP', 'DRIO', 'PZRX', 'AKER',
        'YECO'
    ]
    # intrinio = Intrinio()
    # tickers = intrinio.get_stocks()

    # tickers = pickle.load(open("pickles/stocks_less_than_500m.p", "rb"))
    #tickers = tickers[:400]

    # Create universe
    my_universe = Universe(tickers, "Normal < 200m")

    # Blacklist certain stocks
    my_universe.blacklist(['BURG', 'CVM.W', 'AGM.A'])

    # Create dataframes from universe. Uses threads and multiprocessing
    stocks = build_dataframes(
        my_universe)  # => weird multidimensional list of stocks

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
