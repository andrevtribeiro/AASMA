

class Item:

    def __init__(self, item_id, sell_price, buy_price=None, expiry_date_dd_mm_aaaa=None, item_name=None):
        self.id = item_id
        self.name = item_name or ""
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.expiry_date = expiry_date_dd_mm_aaaa

    def getID(self):
        return self.id

    def getExpiryDate(self):
        return self.expiry_date

    def getBuyPrice(self):
        return self.buy_price

    def getSellPrice(self):
        return self.sell_price

    def __repr__(self):
        return "Item -> " + str(self.id) + " - BUY_PRICE -> " + str(self.buy_price) + " SELL_PRICE -> " + str(self.sell_price) + " - " + str(self.expiry_date)


# example Item
example_item = Item(1, 1, 3, "30-06-2020","FRUIT",)

