from strategy import *


class SMACrossOver(Strategy):
    def __init__(self, name):
        super(SMACrossOver, self).__init__(name)
        self.body = 0
        self.bear_shadow = 0
        self.name = name

    def get_buy_coordinates(self, df):
        buy_locations = df.index[
            (df['sma100'] > df['sma400']) &
            (df['sma100'].shift(1) < df['sma400'].shift(1)) &
            (df['volume'] > 50000) & # 50k not enough. use > 100k to rid of false alarms
            # (df['rel_vol_20p'] > 23) & # The higher the market cap the less relative volume there would be
            (df['rel_vol_100p'] > 5) # The higher the market cap the less relative volume you have to target
        ]
        print buy_locations

        return buy_locations

    @staticmethod
    def check_for_conditions(self, df, ticker, buy_locations):
            if len(buy_locations) == 0:
                pass

    def sell_algorithm(self, init, ticker, df):
        sell_price = 0
        sell_date = 0
        print 'ticker'.format(ticker)
        for i in range(init, len(df)):

            if (df.iloc[[i]]['sma100'] > df.iloc[[i]]['sma400']).values[0]:
                continue

            elif (df.iloc[[i]]['sma100'] < df.iloc[[i]]['sma400']).values[0] and\
                 (df.iloc[[i-1]]['sma100'] > df.iloc[[i-1]]['sma400']).values[0]:
                sell_price = df.iloc[[i]]['close'].values[0]
                sell_date = df.iloc[[i]]['date'].values[0]
                print 'SELL date: {0}'.format(sell_date)
                print 'SELL PRICE: {0}'.format(sell_price)

                break
        return sell_date, sell_price