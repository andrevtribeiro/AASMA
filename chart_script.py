import main
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np

def run(name_sell_dec, name_buy_dec, agent_risk, risk_list, money_list, cashflow_list, loss_in_orders_list,
        loss_in_expired_list, sum_of_loss_list, avg_orders_gelado_list, avg_orders_cha_list,mutex):
    print("Risk -> " + str(agent_risk))
    # risk in range [0,1]
    agent_risk = agent_risk / 100
    
    # missing: avg buys per day, avg price of avg prices of sellers
    money_result, cashflow_result, loss_in_orders_result, loss_in_expired_result, sum_of_loss, avg_orders_gelado, avg_orders_cha = main.main(
        agent_risk, name_sell_dec, name_buy_dec, 0)

    # updates
    mutex.acquire()
    risk_list.append(agent_risk)
    money_list.append(money_result)
    cashflow_list.append(cashflow_result)
    loss_in_orders_list.append(loss_in_orders_result)
    loss_in_expired_list.append(loss_in_expired_result)
    sum_of_loss_list.append(sum_of_loss)
    avg_orders_gelado_list.append(avg_orders_gelado)
    avg_orders_cha_list.append(avg_orders_cha)
    mutex.release()


def charting(name_sell_dec, name_buy_dec, risk_list, money_list, cashflow_list, loss_in_orders_list,
             loss_in_expired_list, sum_of_loss_list, avg_orders_gelado_list, avg_orders_cha_list):
    # Charting
    order = np.argsort(risk_list)
    df = pd.DataFrame({"Risk": np.array(risk_list)[order], "Money": np.array(money_list)[order],
                       "CashFlow": np.array(cashflow_list)[order],
                       "Lost Money on Unfulfilled Orders": np.array(loss_in_orders_list)[order],
                       "Lost Money of Expired Stock": np.array(loss_in_expired_list)[order],
                       "Sum of Losses": np.array(sum_of_loss_list)[order],
                       "Avg Gelado": np.array(avg_orders_gelado_list)[order],
                       "Avg Cha": np.array(avg_orders_cha_list)[order]})

    # plotting results

    # chart money
    plt.title('Money per Risk')
    plt.xlabel('Risk')
    plt.ylabel('Money')
    plt.plot("Risk", "Money", data=df)
    plt.savefig('results/' + name_buy_dec + "_" + name_sell_dec + "_ " + 'risk_money_chart.png')
    plt.close()

    # chart cashflow
    plt.title('Cashflow per Risk')
    plt.xlabel('Risk')
    plt.ylabel('Cashflow')
    plt.plot("Risk", "CashFlow", data=df)
    plt.legend()
    plt.savefig('results/' + name_buy_dec + "_" + name_sell_dec + "_ " + 'risk_cashflow_chart.png')
    plt.close()

    # chart lost money
    plt.title('Lost Money per Risk')
    plt.xlabel('Risk')
    plt.ylabel('Lost Money')
    plt.plot("Risk", "Lost Money on Unfulfilled Orders", data=df, color="blue")
    plt.plot("Risk", "Lost Money of Expired Stock", data=df, color="green")
    plt.plot("Risk", "Sum of Losses", data=df, color="red")
    plt.legend()
    plt.savefig('results/' + name_buy_dec + "_" + name_sell_dec + "_ " + 'risk_loss_chart.png')
    plt.close()

    # chart Avg gelado
    plt.title('Avg Gelado per Risk')
    plt.xlabel('Risk')
    plt.ylabel('Avg Gelado')
    plt.plot("Risk", "Avg Gelado", data=df)
    plt.legend()
    plt.savefig('results/' + name_buy_dec + "_" + name_sell_dec + "_ " + 'risk_avg_gelado_chart.png')
    plt.close()

    # chart Avg cha
    plt.title('Avg Cha per Risk')
    plt.xlabel('Risk')
    plt.ylabel('Avg Cha')
    plt.plot("Risk", "Avg Cha", data=df)
    plt.legend()
    plt.savefig('results/' + name_buy_dec + "_" + name_sell_dec + "_ " + 'risk_avg_cha_chart.png')
    plt.close()


if __name__ == '__main__':

    with multiprocessing.Manager() as multi_manager:

        mutex = multi_manager.Lock()
        # decision processes
        list_of_sell_dec_processes = ["crescent", "decrescent"]
        list_of_buy_dec_processes = ["MinimizeBuyPrice", "BuyIfXProfit"]

        # Initialization for multiprocessor
        risk_list = multi_manager.list()
        money_list = multi_manager.list()
        cashflow_list = multi_manager.list()
        loss_in_orders_list = multi_manager.list()
        loss_in_expired_list = multi_manager.list()
        sum_of_loss_list = multi_manager.list()
        avg_orders_gelado_list = multi_manager.list()
        avg_orders_cha_list = multi_manager.list()
        processes = []

        # Runs boyz
        n_threads = 5
        for name_sell_dec in list_of_sell_dec_processes:
            for name_buy_dec in list_of_buy_dec_processes:
                # reset for multiprocessor
                risk_list = multi_manager.list()
                money_list = multi_manager.list()
                cashflow_list = multi_manager.list()
                loss_in_orders_list = multi_manager.list()
                loss_in_expired_list = multi_manager.list()
                sum_of_loss_list = multi_manager.list()
                avg_orders_gelado_list = multi_manager.list()
                avg_orders_cha_list = multi_manager.list()
                processes = []
                for batch_of_threads in range(1, 100, n_threads):
                    for agent_risk in range(batch_of_threads, batch_of_threads + n_threads, 1):
                        p = multiprocessing.Process(target=run, args=(
                        name_sell_dec, name_buy_dec, agent_risk, risk_list, money_list, cashflow_list,
                        loss_in_orders_list, loss_in_expired_list,
                        sum_of_loss_list, avg_orders_gelado_list, avg_orders_cha_list,mutex))
                        p.start()
                        processes.append(p)
                    for p in processes:
                        p.join()

                # converts back to list
                risk_list = list(risk_list)
                money_list = list(money_list)
                cashflow_list = list(cashflow_list)
                loss_in_orders_list = list(loss_in_orders_list)
                loss_in_expired_list = list(loss_in_expired_list)
                sum_of_loss_list = list(sum_of_loss_list)
                avg_orders_cha_list = list(avg_orders_cha_list)
                avg_orders_gelado_list = list(avg_orders_gelado_list)

                charting(name_buy_dec, name_sell_dec, risk_list, money_list, cashflow_list, loss_in_orders_list,
                         loss_in_expired_list, sum_of_loss_list, avg_orders_gelado_list, avg_orders_cha_list)
