from Item import Item
from NeuralNetwork import NeuralNetwork
from Warehouse import *
import numpy as np
from Transactions import *
from DecisionProcess import *
import datetime as dt


class BulkOrderTable:
    def __init__(self, quantities, prices, min_price):
        assert (len(quantities) == len(prices)), "BulkOrderTable - Quantities and prices don't have the same length!"
        self.quantities = quantities
        self.prices = prices
        self.min_price = min_price

    # returns price for the desired quantity having in consideration the discount table
    def getOrderPrice(self, quantity):
        price = 0
        for q, p in zip(self.quantities, self.prices):
            if q < quantity:
                price = p
        return price * quantity

    # randomize price increase percentage in mult interval [1.05, 1.15]
    # all prices of bulk increase by the same percentage
    def increasePrice(self):
        increase = np.random.rand() * 0.1
        for i in range(len(self.prices)):
            self.prices[i] *= (1.05 + increase)

    # randomize price decrease percentage in mult interval [0.85, 0.95]
    # all prices of bulk increase by the same percentage
    def decreasePrice(self):
        decrease = np.random.rand() * 0.1
        for i in range(len(self.prices)):
            self.prices[i] = max(self.prices[i] * (0.95 - decrease), self.min_price[i])

    def getAvgPrice(self):
        return sum(self.prices) / len(self.prices)

    def getMinPrice(self):
        return min(self.prices)

    def __repr__(self):
        bulktable = "BulkOrderTable -> [ "
        for entry in range(len(self.quantities)):
            bulktable += str(self.quantities[entry]) + " -> " + str(self.prices[entry]) + "; "
        bulktable = bulktable[:-2]
        bulktable += " ]"
        return bulktable


class Agent:
    def __init__(self, agent_id, agent_name=None):
        self.id = agent_id
        self.name = agent_name or ""

    def __repr__(self):
        return "Agent -> " + str(self.id) + "." + self.name


class Seller(Agent):
    def __init__(self, seller_id, item_id, bulk_order_table, risk=None, seller_name=None):
        super().__init__(seller_id, seller_name)
        self.item_id = item_id
        self.bulk_order_table = bulk_order_table
        # history of prices flutuactions between bulk_order_tables
        self.history_prices = []
        self.history_orders = []
        self.seller_risk = risk or 0.5

    def getClosedAuctionOffer(self):
        return self.bulk_order_table

    def makeOrder(self, quantity):
        self.bulk_order_table.increasePrice()
        self.history_prices += [self.bulk_order_table.getAvgPrice()]
        self.history_orders += [quantity]

    # Notifies seller offer has been denied and so seller decreases price by randomized amount
    def notifySellerOfferDenied(self):
        self.bulk_order_table.decreasePrice()
        self.history_prices += [self.bulk_order_table.getAvgPrice()]
        self.history_orders += [0]

    def notifySellerNoOrder(self):
        self.history_prices += [self.bulk_order_table.getAvgPrice()]
        self.history_orders += [0]

    def getHistoryPrices(self):
        return self.history_prices

    def getHistoryOrders(self):
        return self.history_orders

    def getItemId(self):
        return self.item_id

    def __repr__(self):
        return "Seller -> " + str(self.id) + "." + self.name + " - " + str(self.bulk_order_table) + " - " + str(
            self.item_id)


class Client(Agent):
    def __init__(self, client_id, client_name=None):
        super().__init__(client_id, client_name)

    def __repr__(self):
        return "Client -> " + str(self.id) + "." + self.name


class Manager(Agent):
    def __init__(self, manager_id, warehouse, manager_name=None, risk=None, fulfill_order_decision=None,
                 buy_stock_decision=None):
        super().__init__(manager_id, manager_name)
        # neural network for buying bias
        self.neuralNetwork = NeuralNetwork()
        # average of Day Sales ordered by product Id
        self.avgDaySales = self.getAvgDaySalesFromFile()
        # init warehouse
        self.warehouse = warehouse
        # dict of all different sellers, key is item : value is seller of item
        self.sellers = {}
        self.risk=risk
        if self.risk==None:
            self.risk=0.5
        self.risk_history=[]

        # Decision Processes
        self.fulfill_order_decision = fulfill_order_decision or crescQuantity_crescCustomer()
        self.buy_stock_decision = buy_stock_decision or MinimizeBuyPrice()

        # initialize seller
        for id in self.warehouse.getItemsIds():
            self.sellers[id] = []

    # average of Day Sales ordered by product Id
    def getAvgDaySalesFromFile(self):
        with open('initial_data/avgDaySales.txt', 'r') as f:
            lst = []
            for i in f.readlines():
                lst += [int(i)]
            return lst

    def learnDataset(self, fname):
        self.neuralNetwork.learnFromDataset(fname)

    # predicts bias from input
    def predictBias(self, inputNN):
        return self.neuralNetwork.predict([inputNN])

    # fulfill daily orders
    def fulfillOrders(self, date_dd_mm_aaaa):
        # picks up from orderBook
        dayOrders = self.warehouse.orderbook.getDateOrders(date_dd_mm_aaaa)
        # fulfills regarding priority in fulfill decision Process
        dayOrders.sort(key=lambda ord: self.fulfill_order_decision.decide(ord))
        # fullfill order
        for sorted_order in dayOrders:
            self.warehouse.fulfillOrder(sorted_order)

    # gets dict of all items in the warehouse
    def getWarehouseItems(self):
        return self.warehouse.getItems()

    # add seller to dict of sellers by item
    def addSeller(self, seller):
        assert isinstance(seller, Seller), "Manager add Seller -> seller is not of class Seller"
        self.sellers[seller.getItemId()].append(seller)

    def getItemExpiryTimeAfterBuy(self, item_id):
        return self.warehouse.getItemExpiryTimeAfterBuy(item_id)

    def notifySellersOfferDenied(self, item_id, seller_id_in_item):
        for seller in self.sellers[item_id]:
            if seller_id_in_item != seller.id:
                seller.notifySellerOfferDenied()

    # makes order, update stock, money and cash flow
    def makeBuyOrder(self, seller, order):
        # make seller order
        seller.makeOrder(order.getQuantity())
        # update_stock
        self.warehouse.addBuy(order)

    def getSellPrice_for_item(self, id):
        return self.warehouse.getSellPrice_for_item(id)

    def addNewOrders(self, dayData, day_date, list_items_ids):
        for item_id in list_items_ids:
            for order_of_item in dayData[str(item_id)]:
                new_order = Order(self, Client(order_of_item["client_id"]),
                                  OrderItems(Item(item_id, self.getSellPrice_for_item(item_id)),
                                             order_of_item["quantity"]), day_date)
                self.warehouse.addOrder(new_order)

    def sortedClosedAuctionOffers(self, item_id):
        offers = {}
        for seller in self.sellers[item_id]:
            bot = seller.getClosedAuctionOffer()
            for q, p in zip(bot.quantities, bot.prices):
                offers[p] = [q, seller]
        sorted_prices_list = self.buy_stock_decision.auction_sort(offers)
        return sorted_prices_list, offers

    def notifySellersNoOrder(self, item_id):
        for seller in self.sellers[item_id]:
            seller.notifySellerNoOrder()

    # TODO avaliateDay regarding important metrics
    def perceive_act(self, dayData, day_date):

        """ --------------- PERCEIVE INPUT --------------"""

        # remove listings which date has expired
        self.warehouse.removeExpiredListings(day_date)

        # list of all items ids in warehouse
        list_items_ids = self.warehouse.getItemsIds()

        # Starts by adding orders to order book
        self.addNewOrders(dayData, day_date, list_items_ids)

        # Fulfills day's sell orders
        self.fulfillOrders(day_date)

        #reavaliate risk
        self.risk=self.buy_stock_decision.reavaliate_risk(self.risk,self.warehouse.getLostQuantityinFailedOrders(day_date),self.warehouse.getLostQuantityinExpiredStock(day_date-dt.timedelta(days=1)),sum(self.avgDaySales))
        # predict bias
        bias = []
        sumOfBias = 0

        # calculate bias to be passed as argument for decision process decide buy orders
        for item_id in list_items_ids:
            # decide amounts to buy
            bias += [self.predictBias([item_id] + dayData['events'])]
            if bias[item_id]==0:
                bias[item_id]=0.25
            elif bias[item_id]==6:
                bias[item_id]=5.75
            sumOfBias += bias[item_id]

        """ --------------- ACT ON INPUT --------------"""

        # buy decision process for each item
        for item_id in list_items_ids:
            # do tests changing the value of time in stock
            desired_quantity_to_buy = self.buy_stock_decision.desired_amount(bias[item_id], self.avgDaySales[item_id], self.getItemExpiryTimeAfterBuy(item_id), self.risk, self.warehouse.getStockOfItem(item_id))
            
            # check bulk order table for sellers offers
            prices_list, offers = self.sortedClosedAuctionOffers(item_id)

            buying_from_seller, buy_price, buy_quantity = self.buy_stock_decision.decide(item_id,
                                                                                         desired_quantity_to_buy,
                                                                                         prices_list, offers,
                                                                                         self.warehouse.money,
                                                                                         self.risk, bias[item_id],
                                                                                         (bias[item_id] / sumOfBias),
                                                                                         self.warehouse.getSellPrice_for_item(
                                                                                             item_id),
                                                                                         self.avgDaySales[item_id],
                                                                                         self.warehouse.getStockOfItem(
                                                                                             item_id))
            # if decision process decided to buy
            if buying_from_seller:
                new_item = Item(item_id, self.getSellPrice_for_item(item_id), buy_price,
                                day_date + dt.timedelta(days=self.getItemExpiryTimeAfterBuy(item_id)))
                new_order = Order(buying_from_seller, self, OrderItems(new_item, buy_quantity), day_date)
                self.makeBuyOrder(buying_from_seller, new_order)
                # notifies all sellers except buying from seller
                self.notifySellersOfferDenied(item_id, buying_from_seller.id)
                self.warehouse.real_buy_orders[item_id].append(self.warehouse.ledger.getDayAmountOfBuy(day_date, item_id))
            else:
                # notifies all sellers
                self.notifySellersNoOrder(item_id)

            """ ------------- History and Charting ---------------------"""
            
            self.warehouse.stock_after_order_history[item_id].append(self.warehouse.getStockOfItem(item_id))

            # Amount of Buy per Item
            self.warehouse.buy_orders[item_id].append(self.warehouse.ledger.getDayAmountOfBuy(day_date, item_id))

            # Warehouse Finances
        self.warehouse.money_history.append(self.warehouse.money)
        self.warehouse.cashflow_history.append(self.warehouse.cashflow)
        self.warehouse.lostmoney_orders_history.append(self.warehouse.getLostMoneyinFailedOrders())
        self.warehouse.lostmoney_stock_history.append(self.warehouse.getLostMoneyinExpiredStock())
        self.risk_history.append(self.risk)
