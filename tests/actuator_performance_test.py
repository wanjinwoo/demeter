from datetime import datetime, date
from decimal import Decimal

from demeter import TokenInfo, PoolBaseInfo, Actuator, Strategy, Asset, ChainType
from demeter.broker.liquitidymath import get_sqrt_ratio_at_tick
import time


# https://polygonscan.com/tx/0x288f2e2d123ffa2b041cce53962c064c134a14bb2be1793b2e5b0c518f4eb00f
class ActualStrategy(Strategy):
    def on_bar(self, row_data):
        if row_data.timestamp == datetime(2022, 6, 6, 11, 5):
            p, lower, upper, l = self.broker.add_liquidity_by_tick(200670,
                                                                   200930,
                                                                   Decimal("315.218605"),
                                                                   Decimal("0.135641006407938685"),
                                                                   get_sqrt_ratio_at_tick(200786))


if __name__ == "__main__":
    eth = TokenInfo(name="eth", decimal=18)
    usdc = TokenInfo(name="usdc", decimal=6)
    pool = PoolBaseInfo(usdc, eth, 0.05, usdc)
    t1 = time.time()
    actuator = Actuator(pool)
    actuator.strategy = ActualStrategy()
    actuator.set_assets([Asset(usdc, Decimal("315.218605")), Asset(eth, Decimal("0.135641006407938685"))])
    actuator.data_path = "../data"
    actuator.load_data(ChainType.Polygon.name,
                       "0x45dda9cb7c25131df268515131f647d726f50608",
                       date(2022, 6, 6),
                       date(2022, 10, 11))
    actuator.run()
    t2 = time.time()
    print(f"process time {t2 - t1}s")
    actuator.output()
    # for status: AccountStatus in actuator.account_status_list:
    #     print(status)
