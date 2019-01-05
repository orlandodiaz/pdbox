
"""
This file has utilities that are used in the backtesting process

"""


import talib as ta
import numpy as np
import datetime
import pandas as pd
from log3 import log

# Pandas output settings
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)


def make_dataframe_from_csv(ticker):
    """

    Args:
        ticker (str):

    Returns:

    """

    # Path for the ticker Kibot data
    path = '/Users/system-void/gdrive/code/data/stocks/5min/%s.txt' % ticker

    try:
        # Get the size (lines) of file (must open file)
        size = sum(1 for l in open(path))
    except Exception:
        log.error('%7s - Ticker not found in equity database.' % ticker)
        raise
        # raise ValueError('Invalid path to stock files')
    else:
        log.info('%7s - Loading history into memory' % ticker)
        csv_df = pd.read_csv(path, skiprows=range(1, size - 7500))  # Read only the last 7500 lines of the csv
        return csv_df


def correct_csv_df(csv_df):
        # Putting in a format increases performance drastically
        csv_df['date'] = pd.to_datetime(csv_df['date'], format="%m/%d/%Y %H:%M")

        csv_df = csv_df.infer_objects()
        csv_df = csv_df.set_index('date')
        csv_df = csv_df.shift(1)

        # Remove that first row
        csv_df = csv_df.drop(csv_df.index[:1])

        return csv_df


def combine_csv_with_av(csv_df, av_df):
    """ Combines local dataframe from csv with Alphavantage's dataframes

    Args:
        csv_df: Kibot's csv dataframe
        av_df:  Alphavantage dataframe with correct types and datetime as index

    Returns:
        Combined dataframe from both Kibot's csv file andd Alphavantage's time-series API

    Warning. Combining Alphavantage's API with previous historical will cause issues.
    Since alphavantage's data is adjusted every day and your other data is probably not.
    Note this is missing pre-market and after-market data.

    """

    combined_df = pd.concat([csv_df, av_df], axis=0)
    combined_df = combined_df.sort_index()

    return combined_df


def resample_df(df, interval):
    """ Resamples dataframe to use either 2min, 5min, 1hour, daily, or weekly bar
    Args:
        df:
        interval: Either 2min, 5min, 1hour, daily, or weekly

    Returns:

    """

    params = ['2min', '5min', '1hour', 'daily', 'weekly']
    if interval in params:
        conversion = {'open': 'first', 'high': 'max','low': 'min', 'close': 'last', 'volume': 'sum'}

        # Do the conversion
       # df = df.resample('60Min', how=conversion)

    else:
        raise ValueError('The interval you specified was not in the list of allowed intervals.')


def add_columns(df):
    """ Add columns of interest  to dataframes

    Args:
        df: Combined dataframe from both Kibot and AlphaVantage

    Returns:
        df: Returns dataframe with all extra columns of interest such as indicators, etc

    """

    df['sma100'] = df['close'].rolling(window=100).mean()
    df['sma400'] = df['close'].rolling(window=400).mean()

    df['ema13'] = df['close'].ewm(span=13, min_periods=13 - 1).mean()

    vol_sum = 0
    for i in range(0, 20):
        vol_sum = vol_sum + df['volume'].shift(i)

    df['rel_vol_20p'] = df['volume'] / (vol_sum / 20)

    df['rel_vol_20p_2'] = df['volume'] / df['volume'].rolling(window=20).mean()

    vol_sum1 = 0
    for i in range(1, 100):
        vol_sum1 = vol_sum + df['volume'].shift(i)

    df['rel_vol_100p'] = df['volume'] / (vol_sum / 100)


    # df['rel_vol_20p_2'] = df['volume'] / df['volume'].rolling(window=20).mean()

    # df['rel_vol_100p'] = df['volume'] / (vol_sum / 100)
    #
    # df['rel_vol_100p_o'] = df['volume'] / df['volume'].rolling(window=100).mean()

    # df['rel_vol_2day'] = df['volume'] / df['volume'].rolling(window=2).mean()

    vol_sum2 = 0
    for i in range(1, 3):
        vol_sum2 = vol_sum2 + df['volume'].shift(i)

        df['rel_vol_2day'] = df['volume'] / (vol_sum2 / 3)

    # Add Total volume in the previous 7 periods.
    # shift(1) to only include previous 7 datapoints, not including the current one
    df['7dayTotalVol'] = df['volume'].rolling(window=7).sum().shift(1)

    #  df['7dayMaxVol'] = df['volume'].rolling(window=110).max().shift(1) # approximately 2 days

    # Add column taking the absolute difference between the close and open
    df['close_open_diff'] = abs(df['close'] - df['open'])

    # Add column for relative difference between current CloseOpenDiff and previous windows
    cod_sum = 0
    for i in range(1, 15):
       cod_sum = cod_sum + df['close_open_diff'].shift(i)

    df['rel_close_open_diff'] = df['close_open_diff'] / (cod_sum / 15)

    df['rel_close_open_diff2'] = df['close_open_diff'] / df['close_open_diff'].shift(i).rolling(window=14).mean()

    # Calculates the highest close based on the amount of data we have
    df['1250_window_high'] = df['close'].rolling(window=1250).max().shift(1)

    # Calculates the highest close based on the amount of data we have. 110 gives us better results than 100
    df['4mo_high'] = df['close'].rolling(window="110D").max().shift(1)


    df['7dayMaxVol'] = df['volume'].rolling(window=300).max().shift(1) # approximately 2 days

    df['14period_max_vol'] = df['volume'].rolling(window=30).max().shift(1) # 3 bars behind

    df['ema_deviation'] = df['close'] / df['ema13']

    df['pct_change'] = ((df['close'] - df['open'])  / df['open']) * 100

    df['avg_vol_14d'] = df['volume'].rolling(window="14D").mean().shift(1)
    #df['avg_vol_50d'] = df['volume'].rolling(window="50D").mean().shift(1)

    # df['rel_close_max_diff'] = df['close'] / df['1250_window_high']

    # Row which includes the open for the current day
    df['day_open'] = df.ix[df.index.indexer_between_time(datetime.time(9,30), datetime.time(9,30))]['open']
    df = df.fillna(method='ffill')
    #
    df['chg_since_open'] = ((df['open'] - df['day_open']) / df['day_open']) * 100

    df['adx'] = \
        ta.ADX(np.asarray(df['high']),
               np.asarray(df['low']),
               np.asarray(df['close']),
               timeperiod=14)


    return df
