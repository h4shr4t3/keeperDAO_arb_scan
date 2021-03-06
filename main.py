# ***********************************************************************
#
# DEX Arbitrage Scanner - KeeperDAO application coding challenge ()
#
# Purpose:  Gathering data from several dexes for LP WETH/DAI
#           Build swap price for buy and sell direction for defined swap size (DAI)
#           Check for arbitrage possibility (without consiceration of gas price / tx
#           Log results in CSV File
#
# ***********************************************************************

import requests
import queue
import time
import pandas as pd
from requests.structures import CaseInsensitiveDict
from get_dex_data import GetDexData

# Declaration of token addresses - without leading 0x:

add_WETH = "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
add_DAI = "6b175474e89094c44da98b954eedeac495271d0f"

# Declaration of DEX addresses - without leading 0x:

list_of_dex = [['UniswapV2', 'a478c2975ab1ea89e8196811f51a7b7ade33eb11'],
               ['Sushiswap', 'c3d03e4f041fd4cd388c549ee2a29a9e5075882f'],
               ['Shebaswap', '8faf958e36c6970497386118030e6297fff8d275'],
               ['Sakeswap', '2ad95483ac838e2884563ad278e933fba96bc242'],
               ['Croswap', '60a26d69263ef43e9a68964ba141263f19d71d51']]

# Declaration of trading size for seek of arbitrage opportunity
swap_size = 3000      # swap size in DAI

# Declaration of lists for estimated buy and sell prices
list_of_sell_prices = []
list_of_buy_prices = []

# Initializing Queue for DEX threads
c_queue = queue.Queue()
cycle_q = c_queue


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

# Start of implementation

n_dex = len(list_of_dex)        # getting number of dex's to scan
while True:     # do forever
    bn = get_blocknumber()          # get block number (used as index for CSV file)
    list_of_sell_prices = []
    list_of_buy_prices = []
    list_of_headers = []
    list_of_values = []
    # initialize individual threads for gathering data from DEXs to save some time for curl calls
    for iThread in range(0, n_dex, 1):
        thread_name = list_of_dex[iThread][0]
        thread_no = iThread + 1
        thread = GetDexData(thread_no, thread_name, cycle_q)
        thread.set_params(list_of_dex[iThread][0], list_of_dex[iThread][1], swap_size)
        print("New dex thread started for " + thread_name)
        thread.start()

    dex_data_received = 0       # resetting number of DEXs scanned

    # check for return results from all open threads
    while dex_data_received < n_dex:
        while not cycle_q.empty():
            cycle_item = cycle_q.get()
            dex_data_received += 1
            # fit results into sub lists
            sell_item = ["SELL_" + cycle_item[0], cycle_item[1]]
            list_of_sell_prices.append(sell_item)
            buy_item = ["BUY_" + cycle_item[0], cycle_item[2]]
            list_of_buy_prices.append(buy_item)
            list_of_headers.append("SELL_" + cycle_item[0])
            list_of_headers.append("BUY_" + cycle_item[0])
            list_of_values.append(cycle_item[1])
            list_of_values.append(cycle_item[2])
            print('Got data from : ' + cycle_item[0])

    print('Got data from all DEXs')

    # sort sub lists for DEX name (because order before is dependant from thread runtime
    list_of_sell_prices.sort(key=lambda x: x[0])
    list_of_buy_prices.sort(key=lambda x: x[0])
    # combine lists
    complete_list = list_of_buy_prices + list_of_sell_prices
    # check for best buy price and best sell price
    min_buy = min(list_of_buy_prices, key=lambda x: x[1])
    max_sell = max(list_of_sell_prices, key=lambda x: x[1])
    print('Best buy price is $ ' + str(min_buy[1]) + ' @ ' + min_buy[0])
    print('Best sell price is $ ' + str(max_sell[1]) + ' @ ' + max_sell[0])
    profit = 0
    # check for possible arbitrage opportunity
    if min_buy[1] < max_sell[1]:
        profit = round(max_sell[1] / min_buy[1] * swap_size - swap_size, 4)
        print('Profit would be $ ' + str(profit) + ' @ swap size of ' + str(swap_size) + ' DAI')
    else:
        print('No arbitrage opportunity available.')
    # Prepare for export
    list_of_headers.append("block")
    list_of_values.append(bn)
    list_of_headers.append("MinBuy")
    list_of_values.append(min_buy[1])
    list_of_headers.append("MaxSell")
    list_of_values.append(max_sell[1])
    list_of_headers.append("profit")
    list_of_values.append(profit)

    # prepare dataframe for values to add to output file
    df_new = pd.DataFrame([list_of_values], columns=list_of_headers)
    df_new = df_new.set_index('block')
    # get data from file
    df_old = pd.read_csv('logging.csv', index_col='block')
    # concat old and new data
    frames = [df_old, df_new]
    df = pd.concat(frames)
    # export complete dataframe as csv
    df.to_csv('logging.csv', index=True, header=True)

    # wait 5 seconds and repeat
    # avg. block time is about 13.5 seconds
    # so scanning every 5 sec (+ runtime of code execution) should get most of available blocks
    # for now I just want to waste my free compute units from alchemy ;)
    time.sleep(5)
