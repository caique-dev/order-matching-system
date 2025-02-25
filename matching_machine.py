# TODO remove prints from OrderBook methods
# TODO Finish the change order implementation
# TODO Verify the max id in get_buy_order
# TODO implement the change order method
# TODO implement input handling

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        if (order_dict['type'] != 'market' and order_dict['type'] != 'limit'):
                print('This order has an invalid type.')
                return None
        self.type = order_dict['type']

        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                print('This order has an invalid "side".')
                return None
        self.side = order_dict['side']
        
        if (self.type == "limit"):
            if (order_dict['price'] <= 0):
                print('This order has an invalid price.')
                return None

            self.price = order_dict['price']

        if (order_dict['qty'] <= 0):
                print('This order has an invalid quantity.')
                return None
        
        self.qty = order_dict['qty']
    
    def __str__(self):
        print_msg = '(ID: {}) {} {} {} {}'.format(
                self.get_id(),
                self.get_type(),
                self.get_side(),
                self.get_qty(),
                "@ " + str(self.get_price()) if self.type == 'limit' else ''
            )

        return print_msg
    
    def __repr__(self):
        return '(#{}) {} {} {} {}'.format(self.id, self.type, self.side, self.price if self.type == 'limit' else '', self.qty)
    
    def set_id(self, id: int):
        self.id = id

    def get_id(self):
        return self.id

    def get_qty(self):
        return self.qty

    def set_qty(self, qty):
        if (qty > 0):
            self.qty = qty
            return
        
        print('The new quantity is invalid.')

    def get_side(self):
        return self.side

    def get_price(self):
        return self.price

    def set_price(self, price):
        if (price > 0):
            self.price = price
            return
        
        print('The new price is invalid.')

    def get_type(self):
        return self.type

    def is_buy_order(self):
        return self.side == 'buy'

class OrderBook:
    def __init__(self):
        self.order_index = 0
        self.buy_side_dict = {}
        self.sell_side_dict = {}
        self.all_orders_dict = {}

    def add_order(self, order: Order):
        if (order.is_buy_order()):
            order.set_id(self.get_last_order_id())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_order_index()
        else:
            order.set_id(self.get_last_order_id())
            self.sell_side_dict[order.get_id()] = order
            self.incremment_order_index()

        self.all_orders_dict[order.get_id()] = order
        print('Created the order: ', order)

    def cancel_order(self, id: int) -> Order:
        order = self.get_order(id)

        if not (order):
            print('This is an invalid ID.')
        else:
            # removing the order from the general dict
            del self.all_orders_dict[id]

            # removing the order from one of two specific  dict
            if (order.is_buy_order()):
                del self.buy_side_dict[id]
                return order
        
        del self.sell_side_dict[id]
        return order

    def change_order(self, id: int, new_infos: dict):
        if not (id in self.get_all_orders()):
            print('This is an invalid ID.')
            return None
        else: 
            order = self.get_order(id)

            # updating the order's info
            if ('price' in new_infos):
                order.set_price(new_infos['price'])
            if ('qty' in new_infos):
                order.set_qty(new_infos['qty'])
            
            # removing the priority
            self.cancel_order(order.id)             
            self.all_orders_dict[order.id] = order

            if (order.is_buy_order()):
                self.buy_side_dict[order.id] = order
            else:
                self.buy_buy_dict[order.id] = order

    def get_last_order_id(self):
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
        _str = 'Buy Side: \n'
        for order in self.buy_side_dict:
            _str += str(self.buy_side_dict[order]) + '\n'

        _str += 'Sell Side: \n'
        for order in self.sell_side_dict:
            _str += str(self.sell_side_dict[order]) + '\n'
        
        return _str

    def get_order(self, id: int) -> Order:
        if (id in self.all_orders_dict):
            return self.all_orders_dict[id]
    
    def get_all_orders(self) -> dict:
        return self.all_orders_dict


        return None
        

class MatchingMachine:
    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order: dict) -> Order:
        order_obj = Order(order)
        if (order_obj):
            self.book.add_order(order_obj)
        
        return order_obj


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

    def get_order(self, id: int):
        return self.book.get_order(id)

    def cancel_order(self, id: int) -> Order:
        order = self.book.cancel_order(id)
        if (order):
            print('Order cancelled: ', order)

        return order

    def change_order(self, id: int, new_infos: dict):
        self.book.change_order(id, new_infos)

primary_book = OrderBook()
machine = MatchingMachine(primary_book)

teste = machine.add_order({'type': 'limit', 'side': 'buy', 'price': 10, 'qty': 10})

machine.add_order({'type': 'market', 'side': 'sell', 'qty': 20})

machine.add_order({'type': 'limit', 'side': 'buy', 'price': 10, 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 180, 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 160, 'qty': 20})

machine.print_book()
machine.change_order(teste.id, {'price': 1200, 'qty': 10})
machine.print_book()
# print(current_order)

# print(primary_book.get_buy_order())
# print(primary_book.get_sell_order())