from Item import *
import Entities
import datetime as dt


class OrderItems:
    def __init__(self, item, quantity):
        assert isinstance(item, Item), "OrderItems -> item is not of class Item"
        self.item = item
        self.quantity = quantity

    def getItem(self):
        return self.item

    def getItemSellPrice(self):
        return self.item.getSellPrice()

    def getItemBuyPrice(self):
        return self.item.getBuyPrice()

    def getQuantity(self):
        return self.quantity

    def getItemID(self):
        return self.item.getID()

    def getItemExpiryDate(self):
        return self.item.getExpiryDate()

    def __repr__(self):
        return "OrderItems -> " + str(self.item) + " - " + str(self.quantity)


class Order:
    def __init__(self, seller, client, order_items, date_dd_mm_aaaa):
        assert isinstance(client, Entities.Agent), "Order -> client is not of class Agent"
        self.client = client
        assert isinstance(seller, Entities.Agent), "Order -> seller is not of class Agent"
        self.seller = seller
        assert isinstance(order_items, OrderItems), "Order -> order_items is not of class OrderItems"
        self.order_items = order_items
        self.date = date_dd_mm_aaaa

    def getOrderItems(self):
        return self.order_items

    def getOrderItem(self):
        return self.getOrderItems().getItem()

    def getQuantity(self):
        return self.getOrderItems().getQuantity()

    def getItemID(self):
        return self.getOrderItems().getItemID()

    def getDate(self):
        return self.date

    def getSeller(self):
        return self.seller

    def getClient(self):
        return self.client

    def getItemsExpiryDate(self):
        return self.getOrderItems().getItemExpiryDate()

    def getOrderSellPrice(self):
        return self.getQuantity() * self.getOrderItems().getItemSellPrice()

    def getOrderBuyPrice(self):
        return self.getQuantity() * self.getOrderItems().getItemBuyPrice()

    def __repr__(self):
        return "Order => SELLER -> " + str(self.seller) + " CLIENT -> " + str(self.client) + " " + str(self.order_items)


class Transaction:
    def __init__(self, tx_id, order):
        assert isinstance(order, Order), "Transaction -> order is not of class Order"
        self.tx_id = "#TX_" + str(tx_id)
        self.order = order

    def getOrder(self):
        return self.order

    def getTransactionDate(self):
        return self.getOrder().getDate()

    def getTransactionItem(self):
        return self.getOrder().getOrderItem()

    def getTransactionItemID(self):
        return self.getOrder().getItemID()

    def getTransactionQuantity(self):
        return self.getOrder().getQuantity()

    def getTransactionItemsExpriryDate(self):
        return self.getOrder().getItemsExpiryDate()

    def __repr__(self):
        return self.tx_id + " => " + str(self.order)


class Listing:
    def __init__(self, item, quantity):
        assert isinstance(item, Item), "Listing -> item is not of class Item"
        self.item = item
        self.quantity = quantity
        self.id = "#L_" + str(item.id) + "_" + str(item.expiry_date) + "_" + str(self.quantity)

    def getQuantity(self):
        return self.quantity

    def getListingPrice(self):
        return self.item.getBuyPrice() * self.getQuantity()

    def updateQuantity(self, delta_quantity):
        self.quantity += delta_quantity
        self.id = "#L_" + str(self.item.id) + "_" + str(self.item.expiry_date) + "_" + str(self.quantity)

    def getListingItemID(self):
        return self.item.getID()

    def getListingExpiryDate(self):
        return self.item.getExpiryDate()

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return self.id


class Inventory:
    def __init__(self, items_expiryTimeAfterBuy, sellPrice_for_item):
        self.listings = {}
        self.itemsExpiryTimeAfterBuy = items_expiryTimeAfterBuy
        self.sellPrice_for_item = sellPrice_for_item
        self.expired_listings = []

    def getItemsIds(self):
        return list(self.listings.keys())

    def getSellPrice_for_item(self, item_id):
        return self.sellPrice_for_item[item_id]

    def addListing(self, listing):
        assert isinstance(listing, Listing), "Inventory -> add listing is not of class Listing"
        item_id = listing.getListingItemID()
        if item_id in self.listings:
            self.listings[item_id].append(listing)
        else:
            self.listings[item_id] = [listing]

    def removeListing(self, listing):
        assert isinstance(listing, Listing), "Inventory -> remove listing is not of class Listing"
        item_id = listing.getListingItemID()
        # this works after defining __EQ__
        if listing in self.listings[item_id]:
            self.listings[item_id].remove(listing)

    def removeExpiredListings(self, day_date):
        for id in self.listings.keys():
            for listing in self.listings[id]:
                if listing.getListingExpiryDate() < day_date:
                    self.listings[id].remove(listing)
                    self.expired_listings.append(listing)

    def getLostMoneyinExpiredStock(self):
        lost_money = 0
        for listing in self.expired_listings:
            lost_money += listing.getListingPrice()
        return lost_money

    def getLostQuantityinExpiredStock(self,date):
        lost_quantity = 0
        for listing in self.expired_listings:
            if listing.getListingExpiryDate()== (date - dt.timedelta(days=1)):
                lost_quantity += listing.getQuantity()
        return lost_quantity

    # I think this is not used but ill leave it here
    def updateListing(self, listing, delta_quantity):
        assert isinstance(listing, Listing), "Inventory -> update listing is not of class Listing"
        item_id = listing.getListingItemID()
        if listing in self.listings[item_id]:
            for l in self.listings[item_id]:
                if l == listing:
                    l.updateQuantity(delta_quantity)

    def updateSell(self, transaction):
        assert isinstance(transaction, Transaction), "Inventory -> updateSell transaction is not of class Transaction"
        tx_item_id = transaction.getTransactionItemID()
        tx_quantity = transaction.getTransactionQuantity()
        # sort listings of items per date
        self.listings[tx_item_id].sort(key=lambda l: l.getListingExpiryDate())
        quantity_left = tx_quantity
        for listing in self.listings[tx_item_id]:
            if listing.getQuantity() < quantity_left:
                quantity_left -= listing.getQuantity()
                self.listings[tx_item_id].remove(listing)
            elif listing.getQuantity() == quantity_left:
                self.listings[tx_item_id].remove(listing)
                return
            else:
                listing.updateQuantity(-quantity_left)
                return

    def updateBuy(self, transaction):
        assert isinstance(transaction, Transaction), "Inventory -> updateBuy transaction is not of class Transaction"
        tx_item_id = transaction.getTransactionItemID()
        tx_quantity = transaction.getTransactionQuantity()
        # verify if theres already a listing with the same expiry date
        flag_updated = 0
        for listing in self.listings[tx_item_id]:
            if not flag_updated:
                if listing.getListingExpiryDate() == transaction.getTransactionItemsExpriryDate():
                    flag_updated = 1
                    listing.updateQuantity(transaction.getTransactionQuantity())
        if not flag_updated:
            new_listing = Listing(transaction.getTransactionItem(), transaction.getTransactionQuantity())
            self.addListing(new_listing)

    def getStockofItem(self, item_id):
        sum_of_available_quantity = 0
        for listing in self.listings[item_id]:
            sum_of_available_quantity += listing.getQuantity()
        return sum_of_available_quantity

    def checkAvailability(self, order):
        assert isinstance(order, Order), "Inventory -> checkavailability order is not of class Order"
        order_item_id = order.getItemID()
        order_quantity = order.getQuantity()
        return self.getStockofItem(order_item_id) >= order_quantity

    def getItemExpiryTimeAfterBuy(self, item_id):
        return self.itemsExpiryTimeAfterBuy[item_id]

    def __repr__(self):
        listings = "Inventory -> "
        for listing in self.listings:
            listings += str(listing) + "; "
        listings = listings[:-2]
        return listings


class Ledger:
    def __init__(self):
        self.buy_txs = {}
        self.sell_txs = {}

    def addBuy(self, buy_tx):
        assert isinstance(buy_tx, Transaction), "buy_tx is not of class Transaction"
        if buy_tx.getTransactionDate() in self.buy_txs:
            self.buy_txs[buy_tx.getTransactionDate()]+=[buy_tx]
        else:
            self.buy_txs[buy_tx.getTransactionDate()]=[buy_tx]

    def addSell(self, sell_tx):
        assert isinstance(sell_tx, Transaction), "sell_tx is not of class Transaction"
        if sell_tx.getTransactionDate() in self.sell_txs:
            self.sell_txs[sell_tx.getTransactionDate()]+=[sell_tx]
        else:
            self.sell_txs[sell_tx.getTransactionDate()]=[sell_tx]

    def getDayAmountOfBuy(self,date,item_id):
        if date in self.buy_txs:
            for buy_tx in self.buy_txs[date]:
                if item_id==buy_tx.getTransactionItemID():
                    return buy_tx.getTransactionQuantity()
        return 0

        
        

    def __repr__(self):
        txs = "Ledger -> \n"
        buy_txs = "Buy_Txs -> "
        for buy in self.buy_txs:
            buy_txs += str(buy) + "; "
        buy_txs = buy_txs[:-2] + "\n"
        sell_txs = "Sell_Txs -> "
        for sell in self.sell_txs:
            sell_txs += str(sell) + "; "
        sell_txs = sell_txs[:-2] + "\n"
        return txs + buy_txs + sell_txs


class OrderBook:
    def __init__(self):
        self.daily_orders = {}
        self.unfulfilledOrders = {}

    # adds new order to the order book, sorted by date
    def addOrder(self, order):
        assert isinstance(order, Order), "order is not of Class Order!"
        order_date = order.getDate()
        if order_date in self.daily_orders:
            self.daily_orders[order_date].append(order)
        else:
            self.daily_orders[order_date] = [order]

    # adds order to unfulfilled orders, sorted by date
    def addunfulfilledOrder(self, order):
        assert isinstance(order, Order), "order is not of Class Order!"
        order_date = order.getDate()
        if order_date in self.unfulfilledOrders:
            self.unfulfilledOrders[order_date].append(order)
        else:
            self.unfulfilledOrders[order_date] = [order]

    # adds list of unfulfilled orders
    def addunfulfilledOrders(self, list_of_orders):
        # list of orders
        if isinstance(list_of_orders, list):
            for order in list_of_orders:
                self.addunfulfilledOrder(order)
        # only one order
        else:
            self.addunfulfilledOrder(list_of_orders)

    # returns amount of money not made in failed orders
    def lostMoneyinFailedOrders(self):
        lost_sell_money = 0
        for date in self.unfulfilledOrders:
            for failed_order in self.unfulfilledOrders[date]:
                lost_sell_money += failed_order.getOrderSellPrice()
        return lost_sell_money

    def lostQuantityinFailedOrders(self,date):
        lost_quantity = 0
        if date in self.unfulfilledOrders:
            for failed_order in self.unfulfilledOrders[date]:
                lost_quantity += failed_order.getQuantity()
        return lost_quantity

    # returns amount of money not made in failed orders
    def dailyLostMoneyinFailedOrders(self, date_dd_mm_aaaa):
        lost_stock_money = 0
        lost_sell_money = 0
        if date_dd_mm_aaaa in self.unfulfilledOrders:
            for failed_order in self.unfulfilledOrders[date_dd_mm_aaaa]:
                lost_stock_money = failed_order.getItemBuyPrice()
                lost_sell_money += failed_order.getItemSellPrice()
        return "TOTAL LOST STOCK MONEY = " + str(lost_stock_money) + " LOST SELL MONEY = " + str(lost_sell_money)

    def getDateOrders(self, date):
        return self.daily_orders[date]

    def getDateUnfulfilledOrders(self, date):
        return self.unfulfilledOrders[date]

    def __repr__(self):
        orderbook = "OrderBook => "
        for date in self.daily_orders:
            orderbook += "Date => " + str(date)
            for order in self.daily_orders[date]:
                orderbook += str(order) + "; "
        orderbook = orderbook[:-2]
        return orderbook
