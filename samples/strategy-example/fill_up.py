import demeter as dt
from datetime import timedelta, date
from demeter import TokenInfo, PoolBaseInfo, Actuator, Asset, AccountStatus, ChainType

from strategy_ploter import plot_position_return_decomposition


class FillUp(dt.Strategy):

    def __init__(self, a=10):
        super().__init__()
        self.a = a
    def initialize(self):
        a = self.a
        P0 = self.broker.pool_status.price
        self.rebalance(P0)  # rebalance all reserve token#

        self.my_a_position = self.add_liquidity(P0 - self.a, P0 + self.a)
        if self.broker.base_asset.balance > 0:
            self.my_b_position = self.add_liquidity(P0 - a, P0)
        else:
            self.my_b_position = self.add_liquidity(P0, P0 + a)

    def on_bar(self, row_data):
        a = self.a
        if row_data.timestamp.hour != 0 or row_data.timestamp.minute != 0:  # every day. need a tool function to set in the future.
            return
        if len(self.broker.positions) > 0:
            keys = list(self.broker.positions.keys())
            for k in keys:
                self.remove_liquidity(k)
            self.rebalance(row_data.price)
        current_price = self.broker.pool_status.price
        self.my_a_position = self.add_liquidity(current_price - self.a, current_price + self.a)
        if self.broker.base_asset.balance > 0:
            self.my_b_position = self.add_liquidity(current_price - a, current_price)
        else:
            self.my_b_position = self.add_liquidity(current_price, current_price + a)

    def rebalance(self, price):
        status: AccountStatus = self.broker.get_account_status(price)
        base_amount = status.net_value / 2
        quote_amount_diff = base_amount / price - status.quote_balance
        if quote_amount_diff > 0:
            self.buy(quote_amount_diff)
        elif quote_amount_diff < 0:
            self.sell(0 - quote_amount_diff)


if __name__ == "__main__":
    eth = TokenInfo(name="eth", decimal=18)
    usdc = TokenInfo(name="usdc", decimal=6)
    pool = PoolBaseInfo(usdc, eth, 0.05, usdc)

    actuator_instance = Actuator(pool)
    actuator_instance.enable_notify = False
    actuator_instance.strategy = FillUp(200)
    actuator_instance.set_assets([Asset(usdc, 2000)])

    actuator_instance.data_path = "../data"
    actuator_instance.load_data(ChainType.Polygon.name,
                              "0x45dda9cb7c25131df268515131f647d726f50608",
                                date(2022, 8, 5),
                                date(2022, 8, 20))
    actuator_instance.run(enable_notify=False)
    print(actuator_instance.final_status.net_value)

    plot_position_return_decomposition(actuator_instance.account_status_list)
