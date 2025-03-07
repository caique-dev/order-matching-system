from Order import Order
from OrderBook import OrderBook
from Utilities import Utilities

class MatchingEngine:
    # statics attributes
    execute_orders = True
    receive_inputs = True

    @staticmethod
    def toggle_trades_state():
        """Pause or resume trades."""
        MatchingEngine.execute_orders = not MatchingEngine.execute_orders

    @staticmethod
    def get_trade_state() -> bool:
        return MatchingEngine.execute_orders

    def __init__(self):
        self.book = OrderBook()

    def add_order(self, order: str) -> Order:
        """Verify, create, and add a new order to the book."""
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
            self.book.add_order(order_obj, MatchingEngine.get_trade_state())
        
        return order_obj

    def partial_trade(self, sell_order_id: int, buy_order_id: int):
        """
        Remove filled orders from the sell/buy/all orders dict and add them to the filled orders dict. Also, update the quantity of unfilled orders.
        """
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
        """Execute limit and pegged buy orders."""
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
                            trade_price = min(
                        sell_order.get_price(), 
                        buy_order_target.get_price()
                    )

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
        """Execute limit and pegged sell orders."""
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
                            trade_price = max(
                        sell_order_target.get_price(), 
                        buy_order.get_price()
                    )

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
        """Execute buy market orders"""
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
        """Execute sell market orders"""
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
        """Verify the type of the order and try to execute it."""
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
        """Get the user input and call handle it."""
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
                    order = self.add_order(command)

                    # trades on
                    if (MatchingEngine.execute_orders and order):
                        order_id = order.get_id()
                        self.try_execute_order(order_id)

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
                    MatchingEngine.toggle_trades_state()
                    Utilities.toggle_out_icon()
                    Utilities.print_message("Trades are currently paused. Type 'resume trade' to resume.")

                elif ('resume' in command):
                    MatchingEngine.toggle_trades_state()
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
        """Infos about the CLI"""
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