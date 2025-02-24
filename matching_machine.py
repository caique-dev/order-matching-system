# TODO Make an unique trade - ask about making different trades for the same order
# TODO Verify the max id in get_buy_order
# TODO implement the change order method
# TODO order creation output

# TODO Rewiew the str of book

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        if (order_dict['type'] != 'market' and order_dict['type'] != 'limit'):
                print('This order has an invalid type.')
                return
        self.type = order_dict['type']

        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                print('This order has an invalid "side".')
                return
        self.side = order_dict['side']
        
        if (self.type == "limit"):
            if (order_dict['price'] <= 0):
                print('This order has an invalid price.')
                return

            self.price = order_dict['price']

        if (order_dict['qty'] <= 0):
                print('This order has an invalid quantity.')
                return
        
        self.qty = order_dict['qty']
    
    def __str__(self):
        if (self.type == 'limit'):
            ret = 'ID: {}, type: {}, side: {}, price: {}, quantity: {}'.format(
                self.id,
                self.type,
                self.side,
                self.price,
                self.qty
            )
        else: 
            ret = 'ID: {},type: {}, side: {}, quantity: {}'.format(
                self.id,
                self.type,
                self.side,
                self.qty
            )

        return ret
    
    def __repr__(self):
        return '{} {} {} {}'.format(self.type, self.side, self.price if self.type == 'limit' else '', self.qty)
    
    def set_id(self, id: int):
        self.id = id

    def get_id(self):
        return self.id

    def get_qty(self):
        return self.qty

    def get_side(self):
        return self.side

    def get_price(self):
        return self.price

    def get_type(self):
        return self.type

    def is_buy_order(self):
        return self.side == 'buy'

class OrderBook:
    def __init__(self):
        self.buy_side_dict = {}
        self.buy_side_index = 0

        self.sell_side_dict = {}
        self.sell_side_index = 0

    def add_order(self, order: Order):
        if (order.is_buy_order()):
            order.set_id(self.get_last_buy_order_id())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_buy_side_index()

            print_msg = 'Order created: (ID: {}) {} {} {} @ {}'.format(
                order.get_id(),
                order.get_type(),
                order.get_side(),
                order.get_qty(),
                order.get_price()
            )
            print(print_msg)
            return
        
        order.set_id(self.get_last_sell_order_id())
        self.sell_side_dict[order.get_id()] = order
        self.incremment_sell_side_index()

        print_msg = 'Order created: (ID: {}) {} {} {}'.format(
            order.get_id(),
            order.get_type(),
            order.get_side(),
            order.get_qty(),
        )
        print(print_msg)



    def remove_order():
        pass

    def get_last_buy_order_id(self):
        return self.buy_side_index
    
    def get_last_sell_order_id(self):
        return self.sell_side_index

    def incremment_buy_side_index(self):
        self.buy_side_index += 1
    
    def incremment_sell_side_index(self):
        self.sell_side_index += 1

    def __str__(self):
        _str = 'Buy Side: \n'
        for order in self.buy_side_vec:
            _str += str(order) + '\n'

        _str += 'Sell Side: \n'
        for order in self.sell_side_vec:
            _str += str(order) + '\n'
        
        return _str

    def get_buy_order(self, id: int = None):
        if (id):
            for elemento in self.buy_side_vec:
                if (elemento.id == id):
                    return elemento

            return None
        
        return self.buy_side_vec.copy()
    
    def get_sell_order(self, id: int = None) -> Order:
        if (id):
            for elemento in self.sell_side_vec:
                if (elemento.id == id):
                    return elemento
            
            return None

        return self.sell_side_vec.copy()

class MatchingMachine:
    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order: dict):
        order_obj = Order(order)
        self.book.add_order(order_obj)

    def buy_limit_order(self, buy_order: Order):
        for sell_order in self.book.get_sell_order():
            if (
                # this order is executed if the ssell price is equal to or lower than the desired buy price
                sell_order.price <= buy_order.price and 
                sell_order.qty >= buy_order.qty
            ):
                # trade 
                price = min(sell_order.price, buy_order.price)
                print("Trade, price: {}, qty: {}".format(price, buy_order.qty))
                return

    def sell_limit_order(self, sell_order: Order):
        for buy_order in self.book.get_buy_order():
            if (
                # this order is executed if the buy price is equal to or greater than the desired sell price
                buy_order.price >= sell_order.price and 
                buy_order.qty >= sell_order.qty
            ):
                # trade 
                price = max(buy_order.price, sell_order.price)
                print("Trade, price: {}, qty: {}".format(price, sell_order.qty))
                return

    def buy_market_order(self, buy_order: Order):
        # ordering the array based on price
        lower_price = self.book.get_sell_order()
        lower_price.sort(key = lambda order : order.price)
        
        for sell_order in lower_price:
            if (
                # this order is executed immediately at the best price found
                sell_order.qty >= buy_order.qty
            ):
                # trade 
                print("Trade, price: {}, qty: {}".format(sell_order.price, buy_order.qty))
                return

    def sell_market_order(self, sell_order: Order):
        # ordering the array based on price
        highest_price = self.book.get_buy_order()
        highest_price.sort(reverse=True, key = lambda order : order.price)
        print(primary_book)
        print(highest_price)
        
        for buy_order in highest_price:
            if (
                # this order is executed immediately at the best price found
                buy_order.qty >= sell_order.qty
            ):
                # trade 
                print("Trade, price: {}, qty: {}".format(buy_order.price, sell_order.qty))
                return

    def print_book(self):
        print(self.book)

primary_book = OrderBook()
machine = MatchingMachine(primary_book)

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 10, 'qty': 10})

machine.add_order({'type': 'market', 'side': 'sell', 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 10, 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 180, 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 160, 'qty': 20})

machine.print_book()
# print(current_order)

# print(primary_book.get_buy_order())
# print(primary_book.get_sell_order())