from backtest.strategy import *
import random


class BuyRandomly(Strategy):
    """Buys and sells at random intervals"""
    def __init__(self, name):
        super(BuyRandomly, self).__init__(name)

        self.name = name
        self.direction = "long"
        self.bar_interval = "5min"

    def get_buy_coordinates(self, df):
        """ Filter out penny stocks and unliquid stocks at the least"""
        buy_locations = df.index[
            (df['close']> 3) &
            (df['volume'] > 200000)  & #50,000 is not a lot of volume to start with. Higher than 100k ensures this is not a false alarm
            (df['avg_vol_14d'] > 200000)
        ]
        return buy_locations

    def sell_algorithm(self,init, ticker, df):
        sell_price = 0
        sell_date = 0
        for i in range(init, len(df)):
            rand_max = random.randint(init, len(df)-1)
            rand_num = random.randint(init,rand_max)
            sell_price = df.iloc[[rand_num]]['close'].values[0]
            sell_date = df.iloc[[rand_num]]['date'].values[0]
            print "%s backtester2: \t %s \t SELL @ %.3f\t LOC: %d . Sold solely on close < ema" \
                  % (dt.now().strftime("%H:%M:%S"), ticker, sell_price, i+1)
            break

        return sell_date, sell_price
