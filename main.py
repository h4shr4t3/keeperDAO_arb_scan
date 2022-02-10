from web3 import Web3
import requests
import pandas as pd
from requests.structures import CaseInsensitiveDict

# Declaration of token addresses - without 0x:

add_WETH = "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
add_DAI = "6b175474e89094c44da98b954eedeac495271d0f"

# Declaration of DEX addresses - without 0x:

add_uniswap = "a478c2975ab1ea89e8196811f51a7b7ade33eb11"
add_sushiswap = "c3d03e4f041fd4cd388c549ee2a29a9e5075882f"
add_shebaswap = "8faf958e36c6970497386118030e6297fff8d275"
add_sakeswap = "2ad95483ac838e2884563ad278e933fba96bc242"
add_croswap = "60a26d69263ef43e9a68964ba141263f19d71d51"

# Declaration of trading size for seek of arbitrage opportunity

swap_size = 10000      # swap size in DAI

def get_blocknumber():
    """ Just getting the latest blocknumber from ETH Mainnet
    Input: none
    Output: blocknumber (int)
    """
    url = "https://eth-mainnet.alchemyapi.io/v2/kNldX6dSLu474Bnfr_EmsEEClld8MCHx"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{"jsonrpc":"2.0","id":"1","method":"eth_blockNumber","params":[]}'

    resp = requests.post(url, headers=headers, data=data).json()

    blocknumber = int(resp['result'], 16)
    print('Current ETH mainnet block number is: ' + str(blocknumber))
    return blocknumber

def get_balances(add_dex, add_token):
    url = "https://eth-mainnet.alchemyapi.io/v2/kNldX6dSLu474Bnfr_EmsEEClld8MCHx"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = '{"jsonrpc": "2.0", "method": "eth_call", "params": [{"data": "0x70a08231000000000000000000000000' + add_dex + '", "to": "0x' + add_token + '"}, "latest"], "id": 1}'

    resp = requests.post(url, headers=headers, data=data).json()
    balance_raw = int(resp['result'], 16)
    balance = round(balance_raw / pow(10, 18), 4)
    return balance

def get_price_impact(bal_weth, bal_dai, size):
    k = bal_weth * bal_dai    # constant product
    old_price = round(bal_dai / bal_weth, 4)
    # sell DAI
    bal_dai_sell = bal_dai - size
    bal_dai_buy = bal_dai + size
    bal_weth_sell = k / bal_dai_sell
    bal_weth_buy = k / bal_dai_buy
    price_sell = round(bal_dai_sell / bal_weth_sell, 4)
    price_buy = round(bal_dai_buy / bal_weth_buy, 4)
    print('Sell price: ' + str(price_sell))
    print('Buy price: ' + str(price_buy))
    return (1-price_sell/old_price)/100



bn = get_blocknumber()
# getting current ETH mainnet block number
print('Current ETH blocknumber is: ' + str(bn))

# getting current equity of UniswapV2
bal_uni_weth = get_balances(add_uniswap, add_WETH)
bal_uni_dai = get_balances(add_uniswap, add_DAI)
print('UniSwapV2 equity of WETH: ' + str(bal_uni_weth))
print('UniSwapV2 equity of DAI: ' + str(bal_uni_dai))

# getting current equity of Sushiswap
bal_sushi_weth = get_balances(add_sushiswap, add_WETH)
bal_sushi_dai = get_balances(add_sushiswap, add_DAI)
print('Sushiswap equity of WETH: ' + str(bal_sushi_weth))
print('Sushiswap equity of DAI: ' + str(bal_sushi_dai))

# getting current equity of Shebaswap
bal_sheba_weth = get_balances(add_shebaswap, add_WETH)
bal_sheba_dai = get_balances(add_shebaswap, add_DAI)
print('Shebaswap equity of WETH: ' + str(bal_sheba_weth))
print('Shebaswap equity of DAI: ' + str(bal_sheba_dai))

# getting current equity of Sakeswap
bal_sake_weth = get_balances(add_sakeswap, add_WETH)
bal_sake_dai = get_balances(add_sakeswap, add_DAI)
print('Sakeswap equity of WETH: ' + str(bal_sake_weth))
print('Sakeswap equity of DAI: ' + str(bal_sake_dai))

# getting current equity of Croswap
bal_cro_weth = get_balances(add_croswap, add_WETH)
bal_cro_dai = get_balances(add_croswap, add_DAI)
print('Croswap equity of WETH: ' + str(bal_cro_weth))
print('Croswap equity of DAI: ' + str(bal_cro_dai))

impact_uni = get_price_impact(bal_uni_weth, bal_uni_dai, swap_size)
impact_sushi = get_price_impact(bal_sushi_weth, bal_sushi_dai, swap_size)
impact_sheba = get_price_impact(bal_sheba_weth, bal_sheba_dai, swap_size)
impact_sake = get_price_impact(bal_sake_weth, bal_sake_dai, swap_size)
impact_cro = get_price_impact(bal_cro_weth, bal_cro_dai, swap_size)

pass