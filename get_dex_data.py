# ***********************************************************************
#
# Threading Class GetDexData()
#
# Purpose:  Getting data from DEX about WETH and DAI and predict prices
#
# ***********************************************************************

import threading
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
        # just setting variables from outside
        self.dex_name = name
        self.add_dex = add
        self.size = size
        pass

    def run(self):
        """ Main function of GetDexData thread
        """
        # get balances for DAI and WETH from chosen DEX LP
        bal_weth = self.get_balances(self.add_dex, self.add_WETH)
        bal_dai = self.get_balances(self.add_dex, self.add_DAI)
        # print(self.dex_name + ' equity of WETH: ' + str(bal_weth))
        # print(self.dex_name + ' equity of DAI: ' + str(bal_dai))
        # now calculate price with standard x*y=k formula
        price_sell, price_buy = self.get_price_impact(bal_weth, bal_dai, self.size)
        # ready to give back results to main thread
        self.queue.put([self.name, price_sell, price_buy])
        pass

    def get_price_impact(self, bal_weth, bal_dai, size):
        """ Just calc the buy and sell price for a chosen swap size (DAI)
                    Input: balance of weth, balance of dai, swap size (DAI)
                    Output: sell price, buy price
        """
        # calc k - factor
        k = bal_weth * bal_dai  # constant product
        old_price = round(bal_dai / bal_weth, 4)  # theoretical price
        # BUY WETH for DAI
        bal_dai_buy = bal_dai + size    # my DAI goes into LP
        bal_weth_buy = k / bal_dai_buy  # WETH from LP goes to me
        price_buy = round(bal_dai_buy / bal_weth_buy, 4)

        # SELL WETH for DAI
        size_weth = size / old_price    # equivalent amount of weth for DAI size
        bal_weth_sell = bal_weth + size_weth    # my WETH goes into LP
        bal_dai_sell = k / bal_weth_sell        # DAI from LP goes to me
        price_sell = round(bal_dai_sell / bal_weth_sell, 4)
        print(self.dex_name + ' - Buy price: ' + str(price_buy) + ' - Swapping ' + str(size) + ' DAI for ' + str(round(bal_weth-bal_weth_buy, 4)) + ' WETH')
        print(self.dex_name + ' - Sell price: ' + str(price_sell) + ' - Swapping ' + str(round(size_weth, 4)) + ' WETH for ' + str(round(bal_dai-bal_dai_sell, 4)) + ' DAI')
        return price_sell, price_buy

    def get_balances(self, add_dex, add_token):
        """ Just getting the balances for given token from given LP
            Input: dex address, token address
            Output: amount of token in LP
        """
        url = "https://eth-mainnet.alchemyapi.io/v2/kNldX6dSLu474Bnfr_EmsEEClld8MCHx"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = '{"jsonrpc": "2.0", "method": "eth_call", "params": [{"data": "0x70a08231000000000000000000000000' + add_dex + '", "to": "0x' + add_token + '"}, "latest"], "id": 1}'

        resp = requests.post(url, headers=headers, data=data).json()
        balance_raw = int(resp['result'], 16)
        balance = round(balance_raw / pow(10, 18), 4)
        return balance
