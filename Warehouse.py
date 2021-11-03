from Transactions import *


class Warehouse:
    def __init__(self, inventory, money=None):
        self.inventory = inventory
        self.ledger = Ledger()
        self.orderbook = OrderBook()
        # counter of Buys
        self.buy_txs_counter = 0
        # counter of Sells
        self.sell_txs_counter = 0
        # initial money to manage
        self.money = money or 1000000
        # initial cash flow (cash flow measures the amount of money moved)
        self.cashflow = 0

        #History for plotting charts
        self.money_history = []
        self.cashflow_history = []
        self.lostmoney_orders_history = []
        self.lostmoney_stock_history = []
        self.buy_orders={}
        self.real_buy_orders={}
        self.stock_after_order_history={}
        for item_id in self.getItemsIds():
            self.buy_orders[item_id]=[]
            self.stock_after_order_history[item_id]=[]
            self.real_buy_orders[item_id]=[]        
            

    def addOrder(self, order):
        assert isinstance(order, Order), "WareHouse addOrder -> order is not of class Order"
        self.orderbook.addOrder(order)

    def fulfillOrder(self, order):
        assert isinstance(order, Order), "WareHouse fulfillOrder -> order is not of class Order"
        # attempt to fulfill
        able_to_fulfill = self.inventory.checkAvailability(order)
        if able_to_fulfill:
            # if he can fulfill
            self.addSell(order)
        else:
            # if he cant fulfill
            self.orderbook.addunfulfilledOrder(order)

    # creates transaction, adds buy to ledger and updates inventory
    def addBuy(self, order):
        assert isinstance(order, Order), "WareHouse Add Buy -> order is not of class Order"
        self.buy_txs_counter += 1
        new_transaction = Transaction(self.buy_txs_counter, order)
        self.inventory.updateBuy(new_transaction)
        self.ledger.addBuy(new_transaction)
        # update money and cashflow
        self.money -= order.getOrderBuyPrice()
        self.cashflow += order.getOrderBuyPrice()

    # creates transaction, adds sell to ledger and updates inventory
    def addSell(self, order):
        assert isinstance(order, Order), "WareHouse Add Sell -> order is not of class Order"
        self.sell_txs_counter += 1
        new_transaction = Transaction(self.sell_txs_counter, order)
        self.inventory.updateSell(new_transaction)
        self.ledger.addSell(new_transaction)
        # update money and cashflow
        self.money += order.getOrderSellPrice()
        self.cashflow += order.getOrderSellPrice()

    # return stock of item by id
    def getStockOfItem(self, item_id):
        return self.inventory.getStockofItem(item_id)

    # returns ids of all items
    def getItemsIds(self):
        return self.inventory.getItemsIds()

    # updates expired inventory
    def removeExpiredListings(self, day_date):
        return self.inventory.removeExpiredListings(day_date)

    # returns item expiry date threshold
    def getItemExpiryTimeAfterBuy(self, item_id):
        return self.inventory.getItemExpiryTimeAfterBuy(item_id)

    def getSellPrice_for_item(self, item_id):
        return self.inventory.getSellPrice_for_item(item_id)

    def getLostMoneyinFailedOrders(self):
        return self.orderbook.lostMoneyinFailedOrders()

    def getLostMoneyinExpiredStock(self):
        return self.inventory.getLostMoneyinExpiredStock()

    def getLostQuantityinFailedOrders(self,date):
        return self.orderbook.lostQuantityinFailedOrders(date)
        
    def getLostQuantityinExpiredStock(self,date):
        return self.inventory.getLostQuantityinExpiredStock(date)