""" ---------------------------------------- ORDER FULFILLING DECISION PROCESS --------------------------------------"""


class FulFillOrderDecisionProcess:
    def __init__(self, rank_of_priorities):
        self.rank_of_priorities = rank_of_priorities

    def decide(self, order):
        return

    def __repr__(self):
        return "I'm deciding to fulfill orders based on " + self.rank_of_priorities


class decrescQuantity_crescCustomer(FulFillOrderDecisionProcess):
    def __init__(self):
        super().__init__("Decrescent Quantity and Crescent Customer ID")

    def decide(self, order):
        # minus for decresc amount
        return - order.getQuantity(), order.client.id


class crescQuantity_crescCustomer(FulFillOrderDecisionProcess):
    def __init__(self):
        super().__init__("Crescent Quantity and Crescent Customer ID")

    def decide(self, order):
        # minus for decresc amount
        return order.getQuantity(), order.client.id


""" ----------------------------------------- BUY STOCK DECISION PROCESS --------------------------------------------"""


class BuyStockDecisionProcess:
    def __init__(self, rank_of_priorities):
        self.rank_of_priorities = rank_of_priorities
        self.risk = 0

    def amount_from_bias(self, bias, avgDaySales):
        if bias == 3:
            return avgDaySales
        elif bias > 3:
            if bias == 6:
                bias = 5.5
            return (3 * avgDaySales) / (6 - bias)
        else:
            if bias == 0:
                bias = 0.5
            return int((bias * avgDaySales) / 3)

    def desired_amount(self, bias, avgDaySales, ItemExpiryTimeAfterBuy, risk, StockOfItem):
        desired_quantity_to_buy = int(self.amount_from_bias(bias, avgDaySales) * ItemExpiryTimeAfterBuy * risk)
        desired_quantity_to_buy -= StockOfItem
        if desired_quantity_to_buy < 0:
            desired_quantity_to_buy = 0
        return desired_quantity_to_buy

    def auction_sort(self, offers):
        return

    def decideIfOrder(self, price, bias, item_id, sell_price, avgDaySales, stock, price_desire):
        return

    def decide(self, item_id, desired_quantity_to_buy, prices_list, offers, warehouse_money, risk, bias,
               intuition_percentage, sell_price, avgDaySales, stock):
        return

    def agent_desire(self, prices_list):
        return

    def reavaliate_risk(self,risk,dayLostMoneyinFailedOrders,dayLostMoneyinExpiredStock,avgDaySales):
        if dayLostMoneyinFailedOrders>dayLostMoneyinExpiredStock:
            increase=0.05*((dayLostMoneyinFailedOrders-dayLostMoneyinExpiredStock)/(avgDaySales))
            risk+=increase
        elif dayLostMoneyinExpiredStock>dayLostMoneyinFailedOrders:
            decrease=0.05*((dayLostMoneyinExpiredStock-dayLostMoneyinFailedOrders)/(avgDaySales))
            risk-=decrease
        if risk<0.01:
            risk=0.01
        elif risk>1:
            risk=1
        return risk

    def __repr__(self):
        return "I'm deciding to buy based on " + self.rank_of_priorities


class MinimizeBuyPrice(BuyStockDecisionProcess):

    def __init__(self):
        super().__init__("Maximizing Orders")

    def auction_sort(self, offers):
        return sorted(offers.keys())


    def decideIfOrder(self, price, bias, item_id, sell_price,avgDaySales,stock,price_desire):
        ordersNextDay = self.amount_from_bias(bias,avgDaySales)
        if price==price_desire and price*1.1 < sell_price:
            return True
        if price * 1.1 < sell_price and ordersNextDay > stock:
            return True
        return False

    def agent_desire(self, prices_list):
        return prices_list[0]

    def decide(self, item_id, desired_quantity_to_buy, prices_list, offers, warehouse_money, risk, bias,
               intuition_percentage, sell_price, avgDaySales, stock):
        price_desire = self.agent_desire(prices_list)
        for price in prices_list:
            maxQuantity = int(min((warehouse_money * risk * intuition_percentage / price, desired_quantity_to_buy)))
            if maxQuantity > offers[price][0]:
                if self.decideIfOrder(price, bias, item_id, sell_price, avgDaySales, stock, price_desire):
                    seller = offers[price][1]
                    return seller, price, maxQuantity
        return None, None, None

        


class BuyIfXProfit(BuyStockDecisionProcess):

    def __init__(self):
        super().__init__("Maximizing Orders")

    def auction_sort(self, offers):
        return sorted(offers.keys())

    # Manager order if the price offered is almost the minimum price he can get
    # and if he does not have enough items for next day
    def decideIfOrder(self, price, bias, item_id, sell_price, avgDaySales, stock, price_desire):
        ordersNextDay = self.amount_from_bias(bias, avgDaySales) * 1
        if price * 1.6 < sell_price:
            return True
        elif price * 1.1 < sell_price and ordersNextDay > stock:
            return True
        return False

    def agent_desire(self, prices_list):
        return prices_list[0]

    def decide(self, item_id, desired_quantity_to_buy, prices_list, offers, warehouse_money, risk, bias,
               intuition_percentage, sell_price, avgDaySales, stock):
        price_desire = self.agent_desire(prices_list)
        for price in prices_list:
            maxQuantity = int(min((warehouse_money * risk * intuition_percentage / price, desired_quantity_to_buy)))
            if maxQuantity > offers[price][0]:
                if self.decideIfOrder(price, bias, item_id, sell_price, avgDaySales, stock, price_desire):
                    seller = offers[price][1]
                    return seller, price, maxQuantity
        return None, None, None
