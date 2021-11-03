from Entities import *
from Warehouse import Warehouse
from DecisionProcess import *
import sys
from Item import *
import json
import datetime as dt
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

PRINT_FLAG = 0


# helper func for disabling or enabling printing
def my_print(args):
    if PRINT_FLAG:
        print(args)


def main(agent_risk, fulfill_order_decision, buy_stock_decision, ChartFlag):
    """ ------------- Restrict Date Interval ---------------------"""

    beginDate = dt.datetime.strptime('01/01/2020', '%d/%m/%Y').date()
    endDate = dt.datetime.strptime('31/12/2022', '%d/%m/%Y').date()

    """ ------------- Initialize Entities, Warehouse and OrderBook ( orderBook not to be fully loaded to memory, its supposed to be read day by day to simulate real behaviour)  ---------------------"""
    # Items and characteristics
    gelado_id = 0
    cha_id = 1
    my_print("Setup Items and Characteristics\n")
    items_expirytimeAfterBuy = {gelado_id: 30, cha_id: 90}
    initial_listings_quantity = {gelado_id: 30000, cha_id: 60000}
    sellPrice_for_item = {gelado_id: 2, cha_id: 1.5}

    # gelado
    gelado = Item(gelado_id, 1, sellPrice_for_item[gelado_id],
                  beginDate + dt.timedelta(days=items_expirytimeAfterBuy[gelado_id]))
    my_print(str(gelado) + "\n")
    # cha
    cha = Item(cha_id, 0.5, sellPrice_for_item[cha_id],
               beginDate + dt.timedelta(days=items_expirytimeAfterBuy[cha_id]))
    my_print(str(cha) + "\n")

    # initial listings
    my_print("Setup Listings\n")
    gelado_listing = Listing(gelado, initial_listings_quantity[gelado_id])
    cha_listing = Listing(cha, initial_listings_quantity[cha_id])
    my_print(str(gelado_listing) + "\n")
    my_print(str(cha_listing) + "\n")

    # initial inventory
    my_print("Setup Inventory\n")
    init_inventory = Inventory(items_expirytimeAfterBuy, sellPrice_for_item)
    my_print(str(init_inventory) + "\n")
    # add Listings to Inventory
    init_inventory.addListing(gelado_listing)
    init_inventory.addListing(cha_listing)

    # initial warehouse
    my_print("Setup Warehouse\n")
    init_warehouse = Warehouse(init_inventory)
    my_print(str(init_warehouse) + "\n")

    """ ------------- Decision Process Initialization ---------------------"""

    if fulfill_order_decision=="crescent":
        fulfill_order_decision=crescQuantity_crescCustomer()
    elif fulfill_order_decision=="decrescent":
        fulfill_order_decision=decrescQuantity_crescCustomer()
    else:
        print(fulfill_order_decision, "wrong fulfill_order_decision")

    if buy_stock_decision=="MinimizeBuyPrice":
        buy_stock_decision=MinimizeBuyPrice()
    elif buy_stock_decision=="BuyIfXProfit":
        buy_stock_decision=BuyIfXProfit()
    else:
        print(buy_stock_decision, "wrong buy_stock_decision")
    
    """ ------------- Agents Initialization and NN training ---------------------"""
    my_print("Setup Manager\n")

    manager = Manager(1, init_warehouse, "MANAGER_BOT", agent_risk, fulfill_order_decision, buy_stock_decision) 
    my_print(str(manager) + "\n")

    my_print("Setup Sellers\n")
    # 3 agents per product gelado
    bot_gelado_1 = BulkOrderTable([1,  15000, 50000], [1.5, 0.75, 0.5], [0.8, 0.5, 0.25])
    seller_gelado_1 = Seller(0, gelado_id, bulk_order_table=bot_gelado_1)
    bot_gelado_2 = BulkOrderTable([1, 30000, 80000], [1.4, 0.7, 0.4], [0.9, 0.4, 0.2])
    seller_gelado_2 = Seller(1, gelado_id, bulk_order_table=bot_gelado_2)
    bot_gelado_3 = BulkOrderTable([1, 15000, 200000], [2, 0.8, 0.3], [1, 0.5, 0.15])
    seller_gelado_3 = Seller(2, gelado_id, bulk_order_table=bot_gelado_3)
    # 3 agents per product cha
    bot_cha_1 = BulkOrderTable([1, 10000, 500000], [1,  0.5, 0.3], [0.5, 0.35, 0.15])
    seller_cha_1 = Seller(0, cha_id, bulk_order_table=bot_cha_1)
    bot_cha_2 = BulkOrderTable([1,  30000, 750000], [1.2, 0.4, 0.2], [0.6, 0.2, 0.13])
    seller_cha_2 = Seller(1, cha_id, bulk_order_table=bot_cha_2)
    bot_cha_3 = BulkOrderTable([1,  20000, 900000], [1.1, 0.35, 0.15], [0.6, 0.3, 0.1])
    seller_cha_3 = Seller(2, cha_id, bulk_order_table=bot_cha_3)
    my_print("Adding Sellers to Manager\n")
    manager.addSeller(seller_gelado_1)
    manager.addSeller(seller_gelado_2)
    manager.addSeller(seller_gelado_3)
    manager.addSeller(seller_cha_1)
    manager.addSeller(seller_cha_2)
    manager.addSeller(seller_cha_3)

    """ ------------- Read Data inititialized before and iterate day by day ---------------------"""

    my_print("Starting file reading and doing real work\n")

    with open('initial_data/daySales.txt') as json_file:
        data = json.load(json_file)

    currentDay = beginDate

    while currentDay != endDate:
        # reads day events and orders from file
        dayData = data[currentDay.strftime("%d/%m/%Y")]

        # takes care of day
        manager.perceive_act(dayData, day_date=currentDay)

        # updates day
        currentDay += dt.timedelta(days=1)

    """ ------------- History and Charting ---------------------"""
    if ChartFlag:
        # Charting
        # days passed
        x_axis = [i for i in range((endDate - beginDate).days)]

        # money chart
        y_money_axis = manager.warehouse.money_history
        # cashflow chart
        y_cashflow_axis = manager.warehouse.cashflow_history
        # lostmoney orders chart
        y_lostmoney_unfulfilled_orders = manager.warehouse.lostmoney_orders_history
        # lostmoney stock chart
        y_lostmoney_stock = manager.warehouse.lostmoney_stock_history
        # sum of losses
        y_sum_of_losses = [i + j for i, j in zip(y_lostmoney_stock, y_lostmoney_unfulfilled_orders)]
        # buy orders per day
        y_buy_orders_gelado = manager.warehouse.buy_orders[gelado_id]
        y_buy_orders_cha = manager.warehouse.buy_orders[cha_id]

        df = pd.DataFrame({"Days": x_axis, "Money": y_money_axis, "CashFlow": y_cashflow_axis,
                           "Lost Money on Unfulfilled Orders": y_lostmoney_unfulfilled_orders,
                           "Lost Money of Expired Stock": y_lostmoney_stock,
                           "Sum of Losses": y_sum_of_losses, "Buy Orders Gelado": y_buy_orders_gelado,
                           "Buy Orders Cha": y_buy_orders_cha,
                           "Stock After Order Gelado":manager.warehouse.stock_after_order_history[gelado_id],
                           "Stock After Order Cha":manager.warehouse.stock_after_order_history[cha_id],
                           "Gelado Seller 1 Prices": seller_gelado_1.getHistoryPrices(),
                           "Gelado Seller 2 Prices": seller_gelado_2.getHistoryPrices(),
                           "Gelado Seller 3 Prices": seller_gelado_3.getHistoryPrices(),
                           "Gelado Seller 1 Orders": seller_gelado_1.getHistoryOrders(),
                           "Gelado Seller 2 Orders": seller_gelado_2.getHistoryOrders(),
                           "Gelado Seller 3 Orders": seller_gelado_3.getHistoryOrders(),
                           "Cha Seller 1 Prices": seller_cha_1.getHistoryPrices(),
                           "Cha Seller 2 Prices": seller_cha_2.getHistoryPrices(),
                           "Cha Seller 3 Prices": seller_cha_3.getHistoryPrices(),
                           "Cha Seller 1 Orders": seller_cha_1.getHistoryOrders(),
                           "Cha Seller 2 Orders": seller_cha_2.getHistoryOrders(),
                           "Cha Seller 3 Orders": seller_cha_3.getHistoryOrders(),
                           "Manager Risk":manager.risk_history })

        # chart money
        plt.xlabel('Days')
        plt.ylabel('Money')
        plt.plot("Days", "Money", data=df)
        plt.savefig('results/money_chart.png')
        plt.close()

        # chart risk
        plt.xlabel('Days')
        plt.ylabel('Risk')
        plt.plot("Days", "Manager Risk", data=df)
        plt.savefig('results/risk_chart.png')
        plt.close()

        # chart cashflow
        plt.xlabel('Days')
        plt.ylabel('Cashflow')
        plt.plot("Days", "CashFlow", data=df)
        plt.legend()
        plt.savefig('results/cashflow_chart.png')
        plt.close()

        # chart lost money

        plt.title('Lost Money')
        plt.xlabel('Days')
        plt.ylabel('Lost Money')
        plt.plot("Days", "Lost Money on Unfulfilled Orders", data=df, color="blue")
        plt.plot("Days", "Lost Money of Expired Stock", data=df, color="green")
        plt.plot("Days", "Sum of Losses", data=df, color="red")
        plt.legend()
        plt.savefig('results/loss_chart.png')
        plt.close()

        # chart buys per day
        fig, (gelado_ax, cha_ax) = plt.subplots(1, 2, figsize=(20, 7))
        gelado_ax.set_title('Gelado')
        gelado_ax.set_xlabel('Days')
        gelado_ax.set_ylabel('Buy Orders')
        gelado_ax.plot("Days", "Buy Orders Gelado", data=df, color="blue")
        cha_ax.set_title('Cha')
        cha_ax.set_xlabel('Days')
        cha_ax.set_ylabel('Buy Orders')
        cha_ax.plot("Days", "Buy Orders Cha", data=df, color="green")
        plt.legend()
        plt.savefig('results/buy_orders_chart.png')
        plt.close()

        # chart stock of item per day
        fig, (gelado_ax, cha_ax) = plt.subplots(1, 2, figsize=(20, 7))
        gelado_ax.set_title('Gelado')
        gelado_ax.set_xlabel('Days')
        gelado_ax.set_ylabel('Stock')
        gelado_ax.plot("Days", "Stock After Order Gelado", data=df, color="red")
        cha_ax.set_title('Cha')
        cha_ax.set_xlabel('Days')
        cha_ax.set_ylabel('Stock')
        cha_ax.plot("Days", "Stock After Order Cha", data=df, color="red")
        plt.legend()
        plt.savefig('results/stock_of_items.png')
        plt.close()

        # chart prices per day for each seller
        fig, (gelado_seller_ax, cha_seller_ax) = plt.subplots(1, 2, figsize=(20, 7))
        gelado_seller_ax.set_title('Gelado')
        gelado_seller_ax.set_xlabel('Days')
        gelado_seller_ax.set_ylabel('Avg Price')
        gelado_seller_ax.plot("Days", "Gelado Seller 1 Prices", data=df, color="blue")
        gelado_seller_ax.plot("Days", "Gelado Seller 2 Prices", data=df, color="red")
        gelado_seller_ax.plot("Days", "Gelado Seller 3 Prices", data=df, color="green")

        cha_seller_ax.set_title('Cha')
        cha_seller_ax.set_xlabel('Days')
        cha_seller_ax.set_ylabel('Avg Price')
        cha_seller_ax.plot("Days", "Cha Seller 1 Prices", data=df, color="blue")
        cha_seller_ax.plot("Days", "Cha Seller 2 Prices", data=df, color="red")
        cha_seller_ax.plot("Days", "Cha Seller 3 Prices", data=df, color="green")
        plt.savefig('results/avg_price_seller_chart.png')
        plt.close()

        # chart quantity ordered per day for each seller
        fig, (gelado_seller_ax, cha_seller_ax) = plt.subplots(1, 2, figsize=(20, 7))
        gelado_seller_ax.set_title('Gelado')
        gelado_seller_ax.set_xlabel('Days')
        gelado_seller_ax.set_ylabel('Orders')
        gelado_seller_ax.plot("Days", "Gelado Seller 1 Orders", data=df, color="blue")
        gelado_seller_ax.plot("Days", "Gelado Seller 2 Orders", data=df, color="red")
        gelado_seller_ax.plot("Days", "Gelado Seller 3 Orders", data=df, color="green")

        cha_seller_ax.set_title('Cha')
        cha_seller_ax.set_xlabel('Days')
        cha_seller_ax.set_ylabel('Orders')
        cha_seller_ax.plot("Days", "Cha Seller 1 Orders", data=df, color="blue")
        cha_seller_ax.plot("Days", "Cha Seller 2 Orders", data=df, color="red")
        cha_seller_ax.plot("Days", "Cha Seller 3 Orders", data=df, color="green")
        plt.savefig('results/orders_seller_chart.png')
        plt.close()

    # returns last money, cash_flow, and losses
    return manager.warehouse.money, \
           manager.warehouse.cashflow, \
           manager.warehouse.getLostMoneyinFailedOrders(), \
           manager.warehouse.getLostMoneyinExpiredStock(), \
           manager.warehouse.getLostMoneyinExpiredStock() + manager.warehouse.getLostMoneyinFailedOrders(), \
           (sum(manager.warehouse.real_buy_orders[gelado_id])/len(manager.warehouse.real_buy_orders[gelado_id])), \
           (sum(manager.warehouse.real_buy_orders[cha_id])/len(manager.warehouse.real_buy_orders[cha_id]))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Arguments are : Risk, selldec, buydec, toChart")
    risk = float(sys.argv[1])
    fulfill_order_decision=sys.argv[2]
    buy_stock_decision=sys.argv[3]
    flagChart = sys.argv[4]

    main(risk, fulfill_order_decision, buy_stock_decision, flagChart)
