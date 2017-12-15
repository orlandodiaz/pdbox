from strategy import *
from lib.log import log

class OversoldMorning(Strategy):
    def __init__(self, name):
        super(OversoldMorning, self).__init__(name)
        self.direction = "long"
        self.bar_interval = "5min"

        self.body = 0
        self.bear_shadow = 0

    def get_buy_coordinates(self, df):
        buy_locations = df.index[
            # (df['chg_since_open'] > 15) &
            # (df['avg_vol_14d'] > 80000) &
            # (df['close'] < df['ema13'])
            (df['close']> 1.0) &
            (df['open']- df['close'] > 0) & # If we have a negative candlestick
            (abs((df['close'] - df['open']) / df['open']) > 0.03) & # with a least .3% pos change. Prevent those low trade dojis
            # (df['rel_close_open_diff'] > 7) & # The candle is much bigger than previous ones. Note: This might not always be the case
            (df['volume'] > 130000) & #50,000 is not a lot of volume to start with. Higher than 100k ensures this is not a false alarm
            # (df['rel_vol_20p'] > 23) & # The higher the market cap the less relative volume there would be
            (df['rel_vol_100p'] > 23) & # The higher the market cap the less relative volume you have to target
            (df['rel_vol_2day'] > 8) &  # use this to prevent getting third or fourth candlesticks which may already be overbought. Don't use for realtime
            (df['7dayTotalVol'] > 4000) &
            # (df.index.time != datetime.time(9,30)) &
            # (df['date'].dt.time != datetime.time(9,30)) & # Alphavantage starts reporting at 9:35
            # (df['high'] > df['4mo_high']) &  # The close is greater than the "7" day high or less depending on the data we have
            ((df['volume'] / df['7dayMaxVol']) > 1.5) & # Not really a 7day high if we don't have enough data. Common issue with alphavantage which only returns the previous 15 days. Previously sued 2.5
            # ... meaning if the breakout happened early we could get as little as 1 day previous high data or no data at all
            (df['low'] / df['close'] < 1.3375)
            # ((df['high'] / df['close'] < 1.1375) & (df['pct_change'] < 0.5)) # Candlestick pattern should not be bearish. Not being hammered down. Greater than 13% indicates it had negative candlesticks in the 1 or 2min
            # (df['close'] / df['ema13'] < 1.35)  #The close is currently NOT deviated more than 45% from its 14-EMA
            # (df['close'] > df['ema13']) # not on bear territory
        ]

        return buy_locations

    @staticmethod
    def check_for_conditions(self, df, ticker, buy_locations):

            if len(buy_locations) == 0:
                # Tells us which conditions failed. Note: Wrong because sometimes multiple conditions are not met
                if (df['volume'] > 130000).any() is False:
                    print '{ticker}\t Volume condition failed. Volume not greater than 130,000'.format(ticker=ticker)
                elif (df['high'] > df['4mo_high']).any() is False:
                    print '{ticker} \t Current high is not greater than the 4 month high'.format(ticker=ticker)
                elif (df['rel_vol_100p'] > 23).any() is False:
                    print 'Relative volume from the last 100 observations is not greater than 23'
                elif ((df['volume'] / df['7dayMaxVol']) > 2.5).any() is False:
                    print('volume is not greater than the 7day maximum volume')

                elif ((df['high'] / df['close']) < 1.1375).any() is False:
                    print 'Bearish candlestick pattern (high over close is greater than 13.76%)'

                # Used to prevent getting 3/4 candlesticks which may already be overbought. Don't use for realtime
                elif(df['rel_vol_2day'] > 8).any() is False:
                    print 'rel_vol_2day is not greater than 8'
                else:
                     print '{ticker} \t a condition failed'.format(ticker=ticker)
                pass

    def sell_algorithm(self,init, ticker, df):
        sell_price = 0
        sell_date = 0
        territory = None
        # determine if on bullish or bear territory
        if df.iloc[init]['close'] > df.iloc[init]['ema13']:
            territory = 'bullish'
        elif df.iloc[init]['close'] < df.iloc[init]['ema13']:
            territory = 'bearish'

        for i in range(init, len(df)):

            if territory == 'bearish':
                if (df.iloc[[i+1]]['close'] > df.iloc[[i+1]]['ema13']).values[0]:
                    sell_price = df.iloc[[i+1]]['close'].values[0]
                    sell_date = df.iloc[[i+1]]['date'].values[0]
                    log.info("%s - SELL @ %.3f\t LOC: %d . Sold solely on close > ema" %(ticker, sell_price, i+1))
                    break
                else:
                    continue

            if territory == 'bullish':
                if (df.iloc[[i + 1]]['close'] < df.iloc[[i + 1]]['ema13']).values[0]:
                    sell_price = df.iloc[[i + 1]]['close'].values[0]
                    sell_date = df.iloc[[i + 1]]['date'].values[0]
                    log.info(
                        "%s - SELL @ %.3f\t LOC: %d . Sold solely on close > ema" % (ticker, sell_price, i + 1))
                    break
                else:
                    continue


            # # If it closes above ema13, keep holding
            # if (df.iloc[[i+1]]['close'] > df.iloc[[i+1]]['ema13']).values[0]:
            #
            #     if self._trade_type == "daily":
            #         # Break loop at the end of the day otherwise
            #         if (df.iloc[[i]]['date'].dt.time >= datetime.time(15,55)).values[0]:
            #             sell_price = df.iloc[[i+1]]['close'].values[0]
            #             sell_date = df.iloc[[i+1]]['date'].values[0]
            #             break
            #         else:
            #             continue
            #     else:
            #         continue
            # else:
            #
            #     # Sell when it closes below ema13
            #     sell_price = df.iloc[[i+1]]['close'].values[0]
            #     sell_date = df.iloc[[i+1]]['date'].values[0]
            #
            #     log.info("%s - SELL @ %.3f\t LOC: %d . Sold solely on close > ema" %(ticker, sell_price, i+1))
            #     break

        return sell_date, sell_price
