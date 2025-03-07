from Utilities import Utilities
from Order import Order

class OrderBook:
    def __init__(self):
        """OrderBook constructor."""
        self.order_index = 0
        
        self.buy_side_dict = {}
        self.sell_side_dict = {}
        self.all_orders_dict = {}
        self.not_executed_orders_dict = {}
        self.filled_orders_dict = {}

    def add_order(self, order: Order, paused_mode):
        """Adds the orders into the buy/sell dict instead of the dict with all orders. If trades are paused, also add the order to a specific dict."""
        if (order.is_buy_order()):
            order.set_id(self.get_order_index())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_order_index()
        else:
            order.set_id(self.get_order_index())
            self.sell_side_dict[order.get_id()] = order
            self.incremment_order_index()

        # updating the offer/bid price
        self.update_index_prices(order)

        self.all_orders_dict[order.get_id()] = order

        # storing the order in the specific dict to execute in priority order when the trade has resumed
        if (paused_mode):
            self.not_executed_orders_dict[order.get_id()] = order

        Utilities.print_message('Order created: {}'.format(order))

    def update_index_prices(self, order: Order):
        """Update the bid and offer price if necessary."""
        if (order.is_limit_order()):
            order_price = order.get_price()

            if (
                order.is_buy_order() and
                (
                    # verifying whether the current price order is highest than offer price 
                    order_price > Order.get_bid_price()
                )
            ):
                Order.update_bid_price(order_price)
            
            if (
                (not (order.is_buy_order())) and
                (
                    # verifying whether the current price order is lowest than offer price 
                    order_price < Order.get_offer_price() or
                    # verifing whether this price was set
                    not (Order.get_offer_price())
                )
            ):
                Order.update_offer_price(order_price)

    def cancel_order(self, id: int) -> Order:
        order = self.get_order(id)

        if not (order):
            Utilities.print_error('2This order not exists.')
        else:
            # removing the order from the general dict
            del self.all_orders_dict[id]

            # removing the order from one of two specific  dict
            if (order.is_buy_order()):
                del self.buy_side_dict[id]
            else:
                del self.sell_side_dict[id]
            
            # verifying if is necessary update the index prices
            if (order.is_limit_order()):
                if (
                    order.is_buy_order() and
                    order.get_price() >= OrderBook.get_bid_price()
                ):
                    buy_arr = self.sort_dict_lim_orders_by_price('buy', reverse=True)
                    
                    if (buy_arr):
                        new_highest_price = buy_arr[0].get_price()
                        # updating the bid price
                        self.update_bid_price(new_highest_price)
                    else: 
                        self.update_bid_price(0)   

                elif (
                    (not order.is_buy_order()) and
                    order.get_price() <= OrderBook.get_offer_price()
                ):
                    sell_arr = self.sort_dict_lim_orders_by_price('sell')

                    if (sell_arr):
                        new_lowest_price = sell_arr[0].get_price()
                        # updating the bid price
                        self.update_offer_price(new_lowest_price)
                    else: 
                        self.update_offer_price(0)                

            return order

    def change_order(self, id: int, new_price: str = '', new_qty: str = '', remove_priority: bool = True) -> bool:
        if not (self.order_exists(id)):
            Utilities.print_error('1This order not exists.')
            return False
        else: 
            order = self.get_order(id)

            # updating the order's info
            if (new_price):
                order.set_price(int(new_price))
            if (new_qty):
                order.set_qty(int(new_qty))
            
            # removing the priority
            if (remove_priority):
                self.cancel_order(order.id)       
                self.all_orders_dict[order.id] = order

                if (order.is_buy_order()):
                    self.buy_side_dict[order.id] = order
                else:
                    self.sell_side_dict[order.id] = order

            # updating the offer/bid prices
            self.update_index_prices(order)
            
            return True

    def add_filled_order(self, order_id: int):
        self.filled_orders_dict[order_id] = self.get_order(order_id)

    def get_not_executed_orders(self):
        return (self.not_executed_orders_dict)

    def reseting_not_executed_dict(self):
        """Remove all orders of the dict."""
        self.not_executed_orders_dict.clear()

    def get_order_index(self) -> int:
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
        """Representation of Orderbook as a string."""
        if (OrderBook.bid_price):
            _str ='\nBid price: {}\n'.format(OrderBook.bid_price)
        else: 
            _str ='\nBid price: not priced yet\n'

        if (OrderBook.offer_price):
            _str +='Offer price: {}\n'.format(OrderBook.offer_price)
        else: 
            _str +='Offer price: not priced yet\n'

        _str += '\nBuy Orders: \n'
        for order in self.buy_side_dict:
            _str += str(self.buy_side_dict[order]) + '\n'

        _str += '\nSell Orders: \n'
        for order in self.sell_side_dict:
            _str += str(self.sell_side_dict[order]) + '\n'
        
        return _str

    def sort_dict_lim_peg_orders_by_price(self, side: str, reverse: bool = False) -> list:
        """
        Take buy/sell side dict orders, create an array with limit and peg orders
        and sort this arr in ascending(default) or decending ordem.
        """
        limit_orders_arr = []

        if ('sell' in side):
            dict_orders = self.get_sell_orders()
        else:
            dict_orders = self.get_buy_orders()

        for order in dict_orders.values():
            if not (order.is_market_order()):
                limit_orders_arr.append(order)

        ret = sorted(
            limit_orders_arr, 
            key= lambda item : item.get_price(), 
            reverse = reverse
        )

        return ret
    
    def sort_dict_lim_orders_by_price(self, side: str, reverse: bool = False) -> list:
        """
        Take buy/sell side dict orders, create an array with only limit orders
        and sort this arr in ascending(default) or decending ordem.
        """
        limit_orders_arr = []

        if ('sell' in side):
            dict_orders = self.get_sell_orders()
        else:
            dict_orders = self.get_buy_orders()

        for order in dict_orders.values():
            if (order.is_limit_order()):
                limit_orders_arr.append(order)

        ret = sorted(
            limit_orders_arr, 
            key= lambda item : item.get_price(), 
            reverse = reverse
        )

        return ret

    def get_order(self, id: int) -> Order:
        """
        Return the order if its exists, otherwise return False
        """
        if (id in self.all_orders_dict):
            return self.all_orders_dict[id]
        
        return False
    
    def get_all_orders(self) -> dict:
        return self.all_orders_dict

    def get_buy_orders(self) -> dict:
        return (self.buy_side_dict)
    
    def get_sell_orders(self) -> dict:
        return (self.sell_side_dict)

    def order_exists(self, id: int) -> bool:
        return (id in self.all_orders_dict)

    def order_exists_filled(self, id: int) -> bool:
        return (id in self.filled_orders_dict)

    def get_filled_order(self, id: int) -> Order:
        if (id in self.filled_orders_dict):
            return self.filled_orders_dict[id]
        
        return False

    def get_all_filled_orders(self) -> dict:
        return (self.filled_orders_dict)
