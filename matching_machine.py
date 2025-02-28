# TODO create pause/pause
# TODO Complete the implementation of the filled orders storage
# TODO implement the method to show more infos about an trade
# TODO implement the update index prices when an order is canceled
# TODO tratment the invalid order

class Utilities:
    @staticmethod
    def print_error(msg: str):
        Utilities.print_message('Error: ' + msg)

    @staticmethod
    def get_input(msg: str = ''):
        if not (msg):
            return input('<< ' + msg)

        return input('<< ' + msg + ': ')

    @staticmethod
    def print_message(msg: str):
        msg_icon = '>> ' if MatchingMachine.get_trade_state() else '==  '
        print(msg_icon + msg)

    @staticmethod
    def sort_dict(dict: dict, reverse: bool = False) -> list:
        return sorted(
            dict.items(), 
            key= lambda items : items[1].get_price(), 
            reverse = reverse
        )

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        # setting type
        if (
            order_dict['type'] == 'market' or 
            order_dict['type'] == 'limit' or
            'peg' in order_dict['type']
        ):
            if ('peg' in order_dict['type']):
                self.type = 'pegged'
            else:
                self.type = order_dict['type']
        else:
            Utilities.print_error('This order has an invalid type.')
            return None

        # setting side
        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                Utilities.print_error('This order has an invalid "side".')
                return None
        self.side = order_dict['side']
        
        # setting price
        if (self.type == "limit"):
            if (
                order_dict['price'].isdigit() and
                float(order_dict['price']) > 0
            ):
                self.price = float(order_dict['price'])
            else:
                Utilities.print_error('This order has an invalid price.')
                return None

        # setting quantity        
        if (
            order_dict['qty'].isdigit() and
            int(order_dict['qty']) > 0
        ):
            self.qty = int(order_dict['qty'])
        else:
            Utilities.print_error('This order has an invalid quantity.')
            return None
    
        # setting ref price
        if (self.type == 'pegged'):
            if (order_dict['ref'] == 'bid' or order_dict['ref'] == 'offer'):
                self.ref = order_dict['ref']
            else:
                Utilities.print_error('This order has a invalid reference price')


    def __str__(self) -> str:
        print_msg = '(ID: {}) {} {} {} un.{}'.format(
                self.get_id(),
                self.get_type(),
                self.get_side(),
                self.get_qty(),
                " @ $" + str(self.get_price()) if self.type != 'market' else ''
            )

        return print_msg
    
    def __repr__(self):
        return '(#{}) {} {} {} {}'.format(
            self.id,
            self.type,
            self.side,
            self.qty,
            '$'+str((self.price)) if (self.type == 'limit') else ('')
        )
    
    def set_id(self, id: int):
        self.id = id

    def get_id(self) -> int:
        return self.id

    def get_qty(self) -> int:
        return self.qty

    def set_qty(self, qty: int):
        if (qty > 0 and qty.is_integer()):
            self.qty = qty
        else:        
            Utilities.print_error('The new quantity is invalid.')

    def get_side(self) -> str:
        return self.side

    def get_price(self) -> float:
        if (self.type == 'pegged'):
            if (self.ref == 'bid'):
                return OrderBook.get_bid_price()
            else:
                return OrderBook.get_offer_price()
        else:
            return self.price

    def set_price(self, price: float):
        if (price > 0):
            self.price = price
        else: 
            Utilities.print_error('The new price is invalid.')

    def get_type(self) -> str:
        return self.type

    def is_buy_order(self) -> bool:
        return (self.side == 'buy')

    def is_pegged_order(self) -> bool:
        return (self.type == 'pegged')

    def is_market_order(self) -> bool:
        return (self.type == 'market')

    def is_limit_order(self) -> bool:
        return (self.type == 'limit')

class OrderBook:
    # static attributes for pegged orders
    bid_price = 0 # highest buy price
    offer_price = 0 # lowest sell price

    def get_bid_price() -> float:
        return OrderBook.bid_price
    
    @staticmethod
    def update_bid_price(value: float):
        OrderBook.bid_price = value

    def get_offer_price() -> float:
        return OrderBook.offer_price
    
    @staticmethod
    def update_offer_price(value: float):
        OrderBook.offer_price = value

    def __init__(self):
        self.order_index = 0
        
        self.buy_side_dict = {}
        self.sell_side_dict = {}
        self.all_orders_dict = {}
        self.filled_orders_dict = {}

    def add_order(self, order: Order):
        if (order.is_buy_order()):
            order.set_id(self.get_last_order_id())
            self.buy_side_dict[order.get_id()] = order
            self.incremment_order_index()
        else:
            order.set_id(self.get_last_order_id())
            self.sell_side_dict[order.get_id()] = order
            self.incremment_order_index()

        # updating the offer/bid price
        self.update_index_prices(order)

        self.all_orders_dict[order.get_id()] = order
        Utilities.print_message('Order created: {}'.format(order))

    def update_index_prices(self, order: Order):
        if (order.is_limit_order()):
            order_price = order.get_price()

            if (
                order.is_buy_order() and
                (
                    # verifying whether the current price order is highest than offer price 
                    order_price > OrderBook.get_bid_price()
                )
            ):
                OrderBook.update_bid_price(order_price)
            
            if (
                (not (order.is_buy_order())) and
                (
                    # verifying whether the current price order is lowest than offer price 
                    order_price < OrderBook.get_offer_price() or
                    # verifing whether this price was set
                    not (OrderBook.get_offer_price())
                )
            ):
                OrderBook.update_offer_price(order_price)


    def cancel_order(self, id: int) -> Order:
        order = self.get_order(id)

        if not (order):
            Utilities.print_error('This order not exists.')
        else:
            # removing the order from the general dict
            del self.all_orders_dict[id]

            # removing the order from one of two specific  dict
            if (order.is_buy_order()):
                del self.buy_side_dict[id]
            else:
                del self.sell_side_dict[id]
            
            # verifying if is necessary update the index prices
            # if (order.is_limit_order()):


            return order

    def change_order(self, id: int, new_price: str = '', new_qty: str = '', remove_priority: bool = True) -> bool:
        if not (self.order_exists(id)):
            Utilities.print_error('This order not exists.')
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

    def get_last_order_id(self):
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
        _str = 'Buy Orders: \n'
        for order in self.buy_side_dict:
            _str += str(self.buy_side_dict[order]) + '\n'

        _str += 'Sell Orders: \n'
        for order in self.sell_side_dict:
            _str += str(self.sell_side_dict[order]) + '\n'
        
        return _str

    def get_order(self, id: int) -> Order:
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

class MatchingMachine:
    # statics attributes
    execute_orders = True
    receive_inputs = True

    @staticmethod
    def togle_trades_state():
        MatchingMachine.execute_orders = not MatchingMachine.execute_orders

    @staticmethod
    def get_trade_state() -> bool:
        return MatchingMachine.execute_orders

    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order: str) -> Order:
        order_arr = (order.strip()).split(' ')

        # orders attributes
        if (len(order_arr) == 4):
            # join the pegged orders attributes
            if ('peg' in order_arr[0]):
                order_dict = {
                    'type': order_arr[0],
                    'ref': order_arr[1],
                    'side': order_arr[2],
                    'qty': (order_arr[3])
                }

            # join the limit order attributes
            else:
                order_dict = {
                    'type': order_arr[0],
                    'side': order_arr[1],
                    'price': (order_arr[2]),
                    'qty': (order_arr[3])
                }
        
        # join the market order attributes
        elif (len(order_arr) == 3):
            order_dict = {
                'type': order_arr[0],
                'side': order_arr[1],
                'qty': (order_arr[2])
            }
        else:
            return None
        
        order_obj = Order(order_dict)

        if (order_obj):
            self.book.add_order(order_obj)
        
        return order_obj

    def add_filled_order(self, order_id: int):
        self.book.add_filled_order(order_id)

    def partial_trade(self, sell_order_id: int, buy_order_id: int):
        sell_order = self.book.get_order(sell_order_id)
        sell_qty = sell_order.get_qty()
        
        buy_order = self.book.get_order(buy_order_id)
        buy_qty = buy_order.get_qty()

        if (sell_qty < buy_qty):
            # the sell order has been filled
            new_buy_qty = buy_qty - sell_qty

            # changing the buy order qty
            self.book.change_order(
                buy_order.get_id(), 
                new_qty = new_buy_qty,
                remove_priority=False
            )

            # removing the filled order of the book
            filled_order = self.book.cancel_order(sell_order.get_id())
        else:
            # buy order has been filled
            new_sell_qty = sell_qty - buy_qty

            # changing the sell order qty
            self.book.change_order(
                sell_order.get_id(), 
                new_qty = new_sell_qty,
                remove_priority=False
            )
            # removing the filled order of the book
            filled_order = self.book.cancel_order(buy_order.get_id())

        self.book.add_filled_order(filled_order.get_id())

    def buy_limit_order(self, id: int) -> bool:
        buy_order_target = self.book.get_order(id)

        for sell_order in self.book.get_sell_orders():
            sell_order = self.book.get_order(sell_order)
            sell_order_price = sell_order.get_price()
        
            # this order is executed if the sell price is equal to or lower than the desired buy price
            if (
                sell_order_price <= buy_order_target.get_price() and
                # verifying whether the pegged order already has a price
                sell_order_price > 0
            ):
                # getting the lowest price between the orders 
                trade_price = min(sell_order.get_price(), buy_order_target.get_price())

                # setting the quantity that was traded
                if (sell_order.get_qty() >= buy_order_target.get_qty()):
                    trade_qty = buy_order_target.get_qty()  
                else: 
                    trade_qty = sell_order.get_qty()

                Utilities.print_message('Trade, price: ${}, qty: {} un.'.format(trade_price, trade_qty))

                # partial trade
                if (buy_order_target.get_qty() != sell_order.get_qty()):
                    self.partial_trade({
                        'sell_order_id': sell_order.get_id(),
                        'buy_order_id': buy_order_target.get_id()
                    })

                    # sinaling if the target order was filled
                    return (buy_order_target.get_qty() > sell_order.get_qty())
                else:
                    # target order was filled executed
                    return False
        else:
            # none of the sell orders hit the price
            return False

    def sell_limit_order(self, id: int) -> bool:
        sell_order_target = self.book.get_order(id)

        for buy_order_id in self.book.get_buy_orders():
            buy_order = self.book.get_order(buy_order_id)
            buy_order_price = buy_order.get_price()

            # this order is executed if the buy price is equal to or greater than the desired sell price
            if (
                buy_order_price >= sell_order_target.get_price() and 
                # verifying whether pegged order already have price
                buy_order_price > 0
            ):
                # getting the highest value between the orders 
                trade_price = max(sell_order_target.get_price(), buy_order.get_price())

                # setting the quantity that was traded
                if (sell_order_target.get_qty() <= buy_order.get_qty()):
                    trade_qty = sell_order_target.get_qty()
                else: 
                    trade_qty = buy_order.get_qty()

                Utilities.print_message('Trade, price: ${}, qty: {} un.'.format(trade_price, trade_qty))

                # partial trade
                if (buy_order.get_qty() != sell_order_target.get_qty()):
                    self.partial_trade(
                        sell_order_id= sell_order_target.get_id(),
                        buy_order_id= buy_order.get_id()
                    )
                    # sinaling if the target order was filled
                    return (sell_order_target.get_qty() > buy_order.get_qty())
                else:
                    # order was completly executed
                    return False
            
        # none of the buy orders hit the price
        return False
            
    def buy_market_order(self, id: int) -> bool:
        buy_order_target = self.book.get_order(id)

        # generating from sell orders dict an ascending sorted array
        lower_price_tuples = Utilities.sort_dict(self.book.get_sell_orders())

        # verifying if the array is not empty
        if (lower_price_tuples):
            sell_order = lower_price_tuples[0][1]
            trade_price = sell_order.get_price()

            # getting the lowest quantity
            trade_qty = min(buy_order_target.get_qty(), sell_order.get_qty())
            
            Utilities.print_message('Trade, price: ${}, qty: {} un.'.format(trade_price, trade_qty))

            # partial trade
            if (buy_order_target.get_qty() != sell_order.get_qty()):
                self.partial_trade(
                    sell_order_id= sell_order.get_id(),
                    buy_order_id= buy_order_target.get_id()
                )

                # sinaling if the target order was filled
                return (buy_order_target.get_qty() > sell_order.get_qty())
            else:
                # target order was completly filled
                return False
        else:
            # there are no more sell ordes
            return False

    def sell_market_order(self, id: int) -> bool:
        sell_order_target = self.book.get_order(id)

        # generating from sell orders dict an ascending sorted array
        highest_price_tuples = Utilities.sort_dict(self.book.get_sell_orders(), reverse=True)

        # verifying if the array is not empty
        if (highest_price_tuples):
            buy_order = highest_price_tuples[0][1]
            trade_price = buy_order.get_price()

            trade_qty = min(sell_order_target.get_qty(), buy_order.get_qty())
            
            Utilities.print_message('Trade, price: ${}, qty: {} un.'.format(trade_price, trade_qty))

            # partial trade
            if (sell_order_target.get_qty() != buy_order.get_qty()):
                self.partial_trade(
                    buy_order_id = buy_order.get_id(),
                    sell_order_id = sell_order_target.get_id()
                )

                # sinaling if the target order was filled
                return (sell_order_target.get_qty() > buy_order.get_qty())
            else:
                # the order was completly filled
                return False
        else:
            # there are no more buy ordes
            return False
        
    def cancel_order(self, id: int) -> Order:
        order = self.book.cancel_order(id)
        if (order):
            Utilities.print_message('Order cancelled.')

        return order

    def try_execute_order(self, id: int):
        if (self.book.order_exists(id)):
                order = self.book.get_order(id)
                try_execute_order_again = False
                
                # trying execute order
                if (order.is_buy_order() and len(self.book.get_sell_orders())):
                    if (order.is_limit_order() or order.is_pegged_order()):
                        try_execute_order_again = self.buy_limit_order(id)
                    else:
                        try_execute_order_again = self.buy_market_order(id)
                elif (len(self.book.get_buy_orders())):
                    if (order.is_limit_order() or order.is_pegged_order()):
                        try_execute_order_again = self.sell_limit_order(id)
                    else:
                        try_execute_order_again = self.sell_market_order(id)

                if (try_execute_order_again):
                    # trying to fill the current order
                    self.try_execute_order(order)
            
    def manual_input_handler(self, direct_command: str = ''):
        # MatchingMachine.help()
        # Utilities.print_message('Enter your orders/commands line by line or comma separated:')
        
        while (MatchingMachine.receive_inputs):
            if (direct_command):
                prompt_input_arr = (direct_command).split(',')
                direct_command = ''
            else:
                prompt_input_arr = (Utilities.get_input()).split(',')

            for command in prompt_input_arr:
                if ('print' in command):
                    print(self.book)

                if ('pause' in command or 'continue' in command):
                    MatchingMachine.togle_trades_state()
                    Utilities.print_message("Trades are currently paused. Type 'continue trade' to resume.")

                elif ('cancel' in command):
                    cmd_arr = command.split(' ')

                    # verification
                    if (cmd_arr[-1].isdigit()):
                        order = self.book.get_order(int(cmd_arr[-1]))
                        # confirmation
                        confirm = Utilities.get_input('Canceling order {}. Are you sure? (yes/no)'.format(order))
                        if (confirm ==  'yes'):
                            self.cancel_order(int(cmd_arr[-1]))
                    else:
                        Utilities.print_error('Invalid ID.')
                
                elif ('change' in command):
                    cmd_arr = command.split(' ')

                    # verifications
                    if (cmd_arr[-1].isdigit()):
                        if (self.book.order_exists(int(cmd_arr[-1]))):
                            order_id = int(cmd_arr[-1])
                        else:
                            Utilities.print_error('This order not exists.')
                    else:
                        Utilities.print_error('This ID is invalid')
                    
                    # changing
                    order = self.book.get_order(order_id)
                    Utilities.print_message('Changing order {}'.format(order))

                    new_price = ''
                    if (order.is_limit_order()):
                        new_price = Utilities.get_input('Enter the new price (press Enter to keep it unchanged)')            

                    new_qty = Utilities.get_input('Enter the new quantity (press Enter to keep it unchanged)')            
                    
                    old_order = str(order)
                    # Changing the order without losing its priority
                    self.book.change_order(
                        order_id,
                        new_price=new_price,
                        new_qty=new_qty
                    )
                    new_order = self.book.get_order(order_id)
                    Utilities.print_message('Order changed: {} -> {}'.format(old_order, new_order))

                elif ('exit' in command):
                    Utilities.print_message('Ending the program...')
                    MatchingMachine.receive_inputs = False
                
                elif ('help' in command):
                    MatchingMachine.help()

                elif ('skip' in command):
                    pass

                # create a new order and try execute
                else:
                    order = self.add_order(command)
                    
                    if (order.get_id() != None):
                        if (MatchingMachine.execute_orders):
                            self.try_execute_order(order.get_id())
                    else:
                        Utilities.print_error('"{}", is an invalid and has been ignored.'.format(command))
    
    @staticmethod
    def help():
        Utilities.print_message('To add a new order: create order <order type (limit/market/pegged)> <order price (just for limit orders)> <order quantity>')
        Utilities.print_message('To change an order: create <order id>')
        Utilities.print_message('To cancel an order: cancel <order id>')
        Utilities.print_message('To print the book: print book')
        Utilities.print_message('To exit the program: exit')


        

primary_book = OrderBook()
machine = MatchingMachine(primary_book)


# primary_book.add_order(Order({'type': 'limit', 'side': 'buy', 'price': '11', 'qty': '10'}))
# machine.add_order('pegged offer sell 100')
# machine.add_order('limit sell 20 10')

machine.manual_input_handler('limit buy 20 10, limit buy 30 10, limit buy 10 10, market sell 10, exit')

print((primary_book.get_sell_orders()))
print(Utilities.sort_dict(primary_book.get_sell_orders()))
# machine.add_order({'type': 'market', 'side': 'sell', 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 9, 'qty': 20})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 180, 'qty': 19})

# machine.add_order({'type': 'limit', 'side': 'buy', 'price': 160, 'qty': 15})

# print(current_order)

# print(primary_book.get_buy_order())
# print(primary_book.get_sell_order())