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
        msg_icon = '>> ' if MatchingEngine.get_trade_state() else '== '
        print(msg_icon + msg)

class Order:
    def __init__(self, order_dict: dict):
        self.id = None

        # setting type
        if not (
            order_dict['type'] == 'market' or 
            order_dict['type'] == 'limit' or
            'peg' in order_dict['type']
        ):
            # Handling the error without exiting the program
            Utilities.print_error('This order has an invalid type.')
            while not (
                order_dict['type'] == 'market' or 
                order_dict['type'] == 'limit' or
                'peg' in order_dict['type']
            ):
                order_dict['type'] = Utilities.get_input('Please, type again')

        if ('peg' in order_dict['type']):
            self.type = 'pegged'
        else:
            self.type = order_dict['type']

        # setting side
        if (order_dict['side'] != 'buy' and order_dict['side'] != 'sell'):
                Utilities.print_error('This order has an invalid "side".')
                while not (order_dict['side'] == 'buy' or order_dict['side'] == 'sell'):
                    order_dict['side'] = Utilities.get_input('Please, type again')

        self.side = order_dict['side']
        
        # setting price
        if (self.type == "limit"):
            if not (
                order_dict['price'].isdigit() and
                float(order_dict['price']) > 0
            ):
                Utilities.print_error('This order has an invalid price.')
                while not (
                    order_dict['price'].isdigit() and
                    float(order_dict['price']) > 0
                ):
                    order_dict['price'] = Utilities.get_input('Please, type again')

            self.price = float(order_dict['price'])

        # setting quantity        
        if not (
            order_dict['qty'].isdigit() and
            int(order_dict['qty']) > 0
        ):
            Utilities.print_error('This order has an invalid quantity.')

            while not (
                order_dict['qty'].isdigit() and
                int(order_dict['qty']) > 0
            ):
                order_dict['qty'] = Utilities.get_input('Please, type again')
        
        self.qty = int(order_dict['qty'])
    
        # setting ref price
        if (self.type == 'pegged'):
            if (order_dict['ref'] == 'bid' or order_dict['ref'] == 'offer'):
                self.ref = order_dict['ref']
            else:
                Utilities.print_error('This order has a invalid reference price')

    def __str__(self) -> str:
        if (self.type != 'market'):
            price = ' @ $' + str(self.get_price())

            # setting a pegged order without price
            if (not self.get_price() and ('peg' in self.type)):
                price = ' @ not priced yet'
        else:
            price = ''
        print_msg = '(ID: {}) {} {} {} un.{}'.format(
                self.get_id(),
                self.get_type(),
                self.get_side(),
                self.get_qty(),
                price
            )

        return print_msg
    
    def __repr__(self):
        return '(#{}) {} {} {} {}'.format(
            self.id,
            self.type,
            self.side,
            self.qty,
            '$'+str((self.get_price())) if (self.type != 'market') else ('')
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
        self.not_executed_orders_dict = {}
        self.filled_orders_dict = {}

    def add_order(self, order: Order, paused_mode):
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
        self.not_executed_orders_dict.clear()

    def get_last_active_order_id(self) -> int:
        """
        Return the id of last created active order
        """
        if (self.all_orders_dict.keys()):
            target_key = list(self.all_orders_dict.keys())[-1]
            return (self.get_all_orders())[target_key].get_id()
    
    def get_order_index(self) -> int:
        """
        Return an avaible order id
        """
        return self.order_index

    def incremment_order_index(self):
        self.order_index += 1

    def __str__(self):
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
        take buy/sell side dict orders, create an array with limit and peg orders
        and sort this arr in ascending(default) or decending ordem
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
        take buy/sell side dict orders, create an array with limit orders
        and sort this arr in ascending(default) or decending ordem
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

class MatchingEngine:
    # statics attributes
    execute_orders = True
    receive_inputs = True

    @staticmethod
    def togle_trades_state():
        MatchingEngine.execute_orders = not MatchingEngine.execute_orders

    @staticmethod
    def get_trade_state() -> bool:
        return MatchingEngine.execute_orders

    def __init__(self):
        self.book = OrderBook()

    def add_order(self, order: str, paused_mode: bool = False) -> Order:
        order_arr = (order.strip()).split(' ')

        # orders attributes
        if (len(order_arr) == 6):
            # join the pegged orders attributes
            if ('peg' in order_arr[-4]):
                order_dict = {
                    'type': order_arr[-4],
                    'ref': order_arr[-3],
                    'side': order_arr[-2],
                    'qty': (order_arr[-1])
                }

            # join the limit order attributes
            else:
                order_dict = {
                    'type': order_arr[-4],
                    'side': order_arr[-3],
                    'price': (order_arr[-2]),
                    'qty': (order_arr[-1])
                }
        
        # join the market order attributes
        elif (len(order_arr) == 5):
            order_dict = {
                'type': order_arr[-3],
                'side': order_arr[-2],
                'qty': (order_arr[-1])
            }
        else:
            return None
        
        order_obj = Order(order_dict)

        if (order_obj):
            self.book.add_order(order_obj, paused_mode)
        
        return order_obj

    def partial_trade(self, sell_order_id: int, buy_order_id: int):
        sell_order = self.book.get_order(sell_order_id)
        sell_qty = sell_order.get_qty()
        
        buy_order = self.book.get_order(buy_order_id)
        buy_qty = buy_order.get_qty()

        if (sell_qty == buy_qty):
            filled_order = self.book.cancel_order(sell_order.get_id())
            self.book.add_filled_order(filled_order)

            filled_order = self.book.cancel_order(buy_order.get_id())
            self.book.add_filled_order(filled_order)
        elif (sell_qty < buy_qty):
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

            self.book.add_filled_order(filled_order.get_id())

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
            sell_order_price = True

            # getting the price of peg/lim orders
            if not (sell_order.is_market_order()):
                sell_order_price = sell_order.get_price()
        
            # this order is executed if the sell price is equal to or lower than the desired buy price
            if (
                (
                    sell_order_price <= buy_order_target.get_price() and
                    # verifying whether the pegged order already has a price
                    sell_order_price > 0
                ) or
                sell_order_price and sell_order.is_market_order()
            ):
                # getting the lowest price between the orders
                if (sell_order.is_market_order()):
                    trade_price = buy_order_target.get_price()
                else:
                    trade_price = min(sell_order.get_price(), buy_order_target.get_price())

                # setting the quantity that was traded
                if (sell_order.get_qty() >= buy_order_target.get_qty()):
                    trade_qty = buy_order_target.get_qty()  
                else: 
                    trade_qty = sell_order.get_qty()

                Utilities.print_message('Trade, price: ${}, qty: {} un. (sell order (ID: {}) and buy order (ID:{}))'.format(
                    trade_price, 
                    trade_qty, 
                    sell_order.get_id(),
                    buy_order_target.get_id()
                ))

                # partial trade
                self.partial_trade(
                    sell_order_id=sell_order.get_id(),
                    buy_order_id=buy_order_target.get_id()
                )

                # sinaling if the target order was filled
                return (buy_order_target.get_qty() > sell_order.get_qty())
        else:
            # none of the sell orders hit the price
            return False

    def sell_limit_order(self, id: int) -> bool:
        sell_order_target = self.book.get_order(id)

        for buy_order_id in self.book.get_buy_orders():
            buy_order = self.book.get_order(buy_order_id)
            buy_order_price = True

            if not (buy_order.is_market_order()):
                buy_order_price = buy_order.get_price()

            # this order is executed if the buy price is equal to or greater than the desired sell price
            if (
                (
                    buy_order_price >= sell_order_target.get_price() and 
                    # verifying whether pegged order already have price
                    buy_order_price > 0
                ) or
                buy_order_price and buy_order.is_market_order()
            ):
                # getting the highest value between the orders 
                if (buy_order.is_market_order):
                    trade_price = sell_order_target.get_price()
                else:
                    trade_price = max(sell_order_target.get_price(), buy_order.get_price())

                # setting the quantity that was traded
                if (sell_order_target.get_qty() <= buy_order.get_qty()):
                    trade_qty = sell_order_target.get_qty()
                else: 
                    trade_qty = buy_order.get_qty()

                Utilities.print_message('Trade, price: ${}, qty: {} un. (sell order (ID: {}) and buy order (ID:{}))'.format(
                    trade_price, 
                    trade_qty, 
                    buy_order.get_id(),
                    sell_order_target.get_id()
                ))

                # partial trade
                self.partial_trade(
                    sell_order_id= sell_order_target.get_id(),
                    buy_order_id= buy_order.get_id()
                )
                # sinaling if the target order was filled
                return (sell_order_target.get_qty() > buy_order.get_qty())
            
        # none of the buy orders hit the price
        return False
            
    def buy_market_order(self, id: int) -> bool:
        buy_order_target = self.book.get_order(id)

        # generating from sell orders dict an ascending sorted array
        lower_price_arr = self.book.sort_dict_lim_peg_orders_by_price('sell')

        # verifying if the array is not empty
        if (lower_price_arr):
            sell_order = lower_price_arr[0]
            trade_price = sell_order.get_price()

            # getting the lowest quantity
            trade_qty = min(buy_order_target.get_qty(), sell_order.get_qty())
            
            Utilities.print_message('Trade, price: ${}, qty: {} un. (sell order (ID: {}) and buy order (ID:{}))'.format(
                    trade_price, 
                    trade_qty, 
                    sell_order.get_id(),
                    buy_order_target.get_id()
            ))

            # partial trade
            self.partial_trade(
                sell_order_id= sell_order.get_id(),
                buy_order_id= buy_order_target.get_id()
            )

            # sinaling if the target order was filled
            return (buy_order_target.get_qty() > sell_order.get_qty())
        else:
            # there are no more sell ordes
            return False

    def sell_market_order(self, id: int) -> bool:
        sell_order_target = self.book.get_order(id)

        # generating from sell orders dict an ascending sorted array
        highest_price_arr = self.book.sort_dict_lim_peg_orders_by_price(
            'buy',
            reverse=True
        )

        # verifying if the array is not empty
        if (highest_price_arr):
            buy_order = highest_price_arr[0]
            trade_price = buy_order.get_price()

            trade_qty = min(sell_order_target.get_qty(), buy_order.get_qty())
            
            Utilities.print_message('Trade, price: ${}, qty: {} un. (sell order (ID: {}) and buy order (ID:{}))'.format(
                    trade_price, 
                    trade_qty, 
                    buy_order.get_id(),
                    sell_order_target.get_id()
                ))

            # partial trade
            self.partial_trade(
                buy_order_id = buy_order.get_id(),
                sell_order_id = sell_order_target.get_id()
            )

            # sinaling if the target order was filled
            return (sell_order_target.get_qty() > buy_order.get_qty())
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

            # This variable signals whether the created order was completely filled or not
            try_execute_order_again = False
            
            # trying execute order
            if (
                order.is_buy_order() and 
                # verifying whether sell orders have already been created
                len(self.book.get_sell_orders())
            ):
                if (order.is_limit_order() or order.is_pegged_order()):
                    try_execute_order_again = self.buy_limit_order(id)
                else:
                    try_execute_order_again = self.buy_market_order(id)
            elif (
                (not order.is_buy_order()) and 
                # verifying whether buy orders have already been created
                len(self.book.get_buy_orders())
            ):
                if not (order.is_market_order):
                    try_execute_order_again = self.sell_limit_order(id)
                else:
                    try_execute_order_again = self.sell_market_order(id)

            if (try_execute_order_again):
                # trying to fill the current order again
                self.try_execute_order(order.get_id())
            
    def manual_input_handler(self, direct_command: str = ''):
        MatchingEngine.help()
        Utilities.print_message('Enter your orders/commands line by line:')
        
        while (MatchingEngine.receive_inputs):
            if (direct_command):
                prompt_input_arr = (direct_command).split(',')
                direct_command = ''
            else:
                prompt_input_arr = (Utilities.get_input()).split(',')

            for command in prompt_input_arr:# create a new order and try execute
                if ('create' in command):
                    # trades on
                    if (MatchingEngine.execute_orders):
                        order = self.add_order(command)
                        order_id = order.get_id()
                    
                        self.try_execute_order(order_id)

                    # trades off
                    else: 
                        order = self.add_order(command, paused_mode = True)

                elif ('print' in command):
                    cmd_arr = command.split(' ')

                    if (len(cmd_arr) == 2):
                        if (cmd_arr[1] == 'book'):
                            print(self.book)
                        
                        elif (cmd_arr[1] == 'filled'):
                            orders = self.book.get_all_filled_orders()
                            
                            if not (orders):
                                Utilities.print_message('no orders have been filled yet')
                            else:
                                for order in orders:
                                    print(order)

                    elif (len(cmd_arr) == 3 and cmd_arr[2].isdigit()):
                        order_id = int(cmd_arr[2])

                        if (self.book.order_exists(order_id)):
                            order = self.book.get_order(order_id)
                            Utilities.print_message(str(order))
                        
                        elif (self.book.order_exists_filled(order_id)):
                            order = self.book.get_order(order_id)
                            Utilities.print_message(str(order))

                    else:
                        Utilities.print_error('Invalid command.')
                                            

                elif ('pause' in command):
                    MatchingEngine.togle_trades_state()
                    Utilities.print_message("Trades are currently paused. Type 'resume trade' to resume.")

                elif ('resume' in command):
                    MatchingEngine.togle_trades_state()
                    Utilities.print_message("Trades have resumed.")

                    # verify whether exist not executed orders
                    for order_id in self.book.get_not_executed_orders():
                        order = self.book.get_order(order_id)
                        self.try_execute_order(order)
                        
                    # reseting the dict of unexecuted orders
                    if (len(self.book.get_not_executed_orders())):
                        self.book.reseting_not_executed_dict()
            
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
                            Utilities.print_error('3This order not exists.')
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
                    MatchingEngine.receive_inputs = False
                
                elif ('help' in command):
                    MatchingEngine.help()

                elif ('skip' in command):
                    pass

                # invalid command
                else:
                    Utilities.print_error('"{}", is an invalid command and has been ignored. Type "help"'.format(command))
    
    @staticmethod
    def help():
        Utilities.print_message('To add a new order: create order [1] [2] [3] [4] [5]')
        Utilities.print_message(' - [1] <order type (limit/market/pegged)> ')
        Utilities.print_message(' - [2] <order index (just for pegged orders)(limit/market/pegged)>')
        Utilities.print_message(' - [3] <order side (sell/buy)>')
        Utilities.print_message(' - [4] <order price (just for limit orders)>')
        Utilities.print_message(' - [5] <order quantity>')
        Utilities.print_message('To change an order: create <order id>')
        Utilities.print_message('To cancel an order: cancel <order id>')
        Utilities.print_message('To print the book: print <book/order/filled (to see the filled ordes)> <order id>')
        Utilities.print_message('To pause the trades: pause')
        Utilities.print_message('To resume the trade: resume')
        Utilities.print_message('To exit the program: exit')
        Utilities.print_message('Type "help" to see these tips again')