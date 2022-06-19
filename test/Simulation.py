import sys

import numpy as np
import pandas as pd
from texttable import Texttable

TRADING_FILE_NAME = 'F:\Stocker\Positional Strategy\Positional.xls'
SIMULATION_COUNT = 100
LOT_SIZE = 50
PER_LOT_CAPITAL = 300000
STARTING_CAPITAL = 25000000
RISK_OF_RUIN = 50


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def get_data():
    data = pd.read_excel(TRADING_FILE_NAME, index_col=None, usecols='O')
    return data.sample(n=210).reset_index(drop=True)


def mdd(returns):
    cum_rets = (1 + returns).cumprod() - 1
    nav = ((1 + cum_rets) * 100).fillna(100)
    hwm = nav.cummax()
    dd = nav / hwm - 1

    return min(dd * 100)


def calculate_cagr(first, last, periods):
    return (last / first) ** (1 / periods) - 1


def print_parameter():
    table = Texttable()
    table.add_rows([['', ''],
                    ['Simulation Count', SIMULATION_COUNT], ['Per Lot Capital', PER_LOT_CAPITAL],
                    ['Opening Balance', STARTING_CAPITAL]
                       , ['Risk Of Ruin', RISK_OF_RUIN]])

    print(table.draw())


def print_result(result_dataframe, risk_ruin_1, risk_of_ruin2):
    dd_table = Texttable()
    dd_table.add_rows([['', 'DrawDown Percent', 'Final Equity (in Crores)', 'calculate_cagr'],
                       ['Mean', result_dataframe.max_dd.mean(), result_dataframe.final_equity.mean(),
                        result_dataframe.calculate_cagr.mean()],
                       ['Median', result_dataframe.max_dd.median(), result_dataframe.final_equity.median(),
                        result_dataframe.calculate_cagr.median()],
                       ['Max', result_dataframe.max_dd.max(), result_dataframe.final_equity.max(),
                        result_dataframe.calculate_cagr.max()],
                       ['Min', result_dataframe.max_dd.min(), result_dataframe.final_equity.min(),
                        result_dataframe.calculate_cagr.min()],
                       ['Worst Case', result_dataframe.max_dd.quantile(0.95),
                        result_dataframe.final_equity.quantile(0.05), result_dataframe.calculate_cagr.quantile(.05)],
                       ['Risk Of Ruin', risk_ruin_1, risk_of_ruin2, 'Not Applicable']
                       ]
                      )
    dd_table.set_cols_align(['l', 'r', 'r', 'r'])
    print(dd_table.draw())


def execute_mc():
    appended_data = []
    count = 0
    risk_ruin_1 = 0
    while (count <= SIMULATION_COUNT):
        progress(count, SIMULATION_COUNT, status='')
        data = get_data()
        simulator = pd.DataFrame(
            columns=['sim_number', 'opening_balance', 'points', 'quantity', 'profit', 'closing_balance'])

        simulator['points'] = data.TP

        for i in range(0, len(simulator)):
            simulator.loc[i, 'sim_number'] = count
            if i == 0:
                simulator.loc[i, 'opening_balance'] = STARTING_CAPITAL
                simulator.loc[i, 'quantity'] = LOT_SIZE
                simulator.loc[i, 'profit'] = np.round(simulator.loc[i, 'quantity'] * simulator.loc[i, 'points'],
                                                      2) - LOT_SIZE * 10
            else:
                simulator.loc[i, 'opening_balance'] = simulator.loc[i - 1, 'closing_balance']
                lot_size = min(max(int(simulator.loc[i, 'opening_balance'] / PER_LOT_CAPITAL), 1), 100)
                simulator.loc[i, 'quantity'] = lot_size * LOT_SIZE
                simulator.loc[i, 'profit'] = np.round(simulator.loc[i, 'quantity'] * simulator.loc[i, 'points'],
                                                      2) - lot_size * 500

            simulator.loc[i, 'closing_balance'] = simulator.loc[i, 'opening_balance'] + simulator.loc[i, 'profit']

        simulator['daily_profit'] = simulator['profit'] / simulator['opening_balance']

        if simulator['closing_balance'].min() < STARTING_CAPITAL * (100 - RISK_OF_RUIN) / 100:
            risk_ruin_1 = risk_ruin_1 + 1

        max_dd = mdd(simulator['daily_profit']) * -1
        sharpe_ratio = simulator.profit.mean() / simulator.profit.std()
        sharpe_ratio = (80 ** .5) * sharpe_ratio
        final_equity = simulator.closing_balance.iloc[-1] / 10000000
        cagr = calculate_cagr(STARTING_CAPITAL, final_equity * 10000000, 1) * 100
        loop_data = [max_dd, np.round(sharpe_ratio), final_equity, cagr]
        appended_data.append(loop_data)
        count = count + 1
    result_dataframe = pd.DataFrame(appended_data, columns=['max_dd', 'sharpe_ratio', 'final_equity', 'calculate_cagr'])
    risk_of_ruin2 = sum(result_dataframe.max_dd >= 50)
    print_result(result_dataframe, risk_ruin_1, risk_of_ruin2)


def monte_carlo():
    print_parameter()
    execute_mc()


def app():
    print('Start')
    monte_carlo()


app()
