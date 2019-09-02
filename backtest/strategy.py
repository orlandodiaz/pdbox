class Strategy(object):

    def __init__(self, name):
        self.name = name
        self.description = None

        # Strategy settings
        self.direction = "long"  # Assuming long strategy as default

        # daily, weekly, monthly
        self._trade_type = "daily"  # Day trader will sell the security during the current trading day no matter what.
        self._after_hours_trading = False  # If true buys during premarket and after-market hours. Not recommended

    def set_description(self, description):
        self.description = description

    def change_direction(self, p_type):
        values = ["short", "long"]
        if p_type not in values:
            print "Invalid position type. Use 'short', or 'long'."
        else:
            self.direction = p_type
