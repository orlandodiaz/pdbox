import os
import cPickle as pickle
import pandas as pd
from log3 import log
BACKTESTS_PATH = "bt_results/"

backtest_log = pd.DataFrame(columns=
            ['timestamp', 'strategy', 'note', 'trade type', 'timeframe', 'stocks','winners','losers', 'win_pct', 'pct_chg_avg'])

# Pandas output settings
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)


def get_backtests():
    for dir_file in os.listdir(BACKTESTS_PATH):
        log.debug("Found file {0}".format(dir_file))
        with open(BACKTESTS_PATH + dir_file, "rb") as f:
            bt = pickle.load(f)
            backtest_log.loc[backtest_log.shape[0]] = [
                bt.timestamp, bt.strategy.name, bt.note, bt.strategy.direction, bt.time_frame, bt.num_of_stocks,
                bt.winners, bt.losers, bt.winning_percent, bt.pct_chg_avg]

    backtest_log.set_index('timestamp', inplace=True)
    backtest_log.sort_index(ascending=False, inplace=True)

    # Fixes misaligned index with headers
    backtest_log.columns.name = backtest_log.index.name
    backtest_log.index.name = None

    print backtest_log

if __name__ == '__main__':
    get_backtests()