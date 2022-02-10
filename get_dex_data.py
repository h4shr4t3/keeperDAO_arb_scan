# ***********************************************************************
#
# Threading Class GetDexData()
#
# Purpose:  Getting data from DEX about WETH and DAI and predict prices
#
# ***********************************************************************


import threading
import time
import copy
import requests
from requests.structures import CaseInsensitiveDict

lock = threading.Lock()


class GetDexData(threading.Thread):
    def __init__(self, threadID, name, queue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.dex_name = ' '
        self.queue = queue
        self.add_dex = ' '
        self.add_WETH = "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        self.add_DAI = "6b175474e89094c44da98b954eedeac495271d0f"
        self.size = 0

    def set_params(self, name, add, size):
        self.dex_name = name
        self.add_dex = add
        self.size = size
        pass

    def run(self):
        bal_weth = self.get_balances(self.add_dex, self.add_WETH)
        bal_dai = self.get_balances(self.add_dex, self.add_DAI)
        print(self.dex_name + ' equity of WETH: ' + str(bal_weth))
        print(self.dex_name + ' equity of DAI: ' + str(bal_dai))
        price_sell, price_buy = self.get_price_impact(bal_weth, bal_dai, self.size)

        self.queue.put([self.name, price_sell, price_buy])
        pass

    def get_price_impact(self, bal_weth, bal_dai, size):
        k = bal_weth * bal_dai  # constant product
        old_price = round(bal_dai / bal_weth, 4)
        # sell DAI
        bal_dai_sell = bal_dai - size
        bal_dai_buy = bal_dai + size
        bal_weth_sell = k / bal_dai_sell
        bal_weth_buy = k / bal_dai_buy
        price_sell = round(bal_dai_sell / bal_weth_sell, 4)
        price_buy = round(bal_dai_buy / bal_weth_buy, 4)
        print(self.dex_name + ' - Sell price: ' + str(price_sell))
        print(self.dex_name + ' - Buy price: ' + str(price_buy))
        return price_sell, price_buy

    def get_balances(self, add_dex, add_token):
        url = "https://eth-mainnet.alchemyapi.io/v2/kNldX6dSLu474Bnfr_EmsEEClld8MCHx"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = '{"jsonrpc": "2.0", "method": "eth_call", "params": [{"data": "0x70a08231000000000000000000000000' + add_dex + '", "to": "0x' + add_token + '"}, "latest"], "id": 1}'

        resp = requests.post(url, headers=headers, data=data).json()
        balance_raw = int(resp['result'], 16)
        balance = round(balance_raw / pow(10, 18), 4)
        return balance
