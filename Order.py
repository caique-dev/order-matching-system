from Utilities import Utilities

class Order:
    # static attributes for pegged orders
    bid_price = 0 # highest buy price
    offer_price = 0 # lowest sell price

    def get_bid_price() -> float:
        return Order.bid_price
    
    @staticmethod
    def update_bid_price(value: float):
        Order.bid_price = value

    def get_offer_price() -> float:
        return Order.offer_price
    
    @staticmethod
    def update_offer_price(value: float):
        Order.offer_price = value

    def __init__(self, order_dict: dict):
        """Order constructor"""
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
        """Representation of the order as a string."""
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
        """Order representation for some areas of VS Code"""
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
        """Return its own price for a limit/market order, or the bid/offer price for pegged orders"""
        if (self.type == 'pegged'):
            if (self.ref == 'bid'):
                return Order.get_bid_price()
            else:
                return Order.get_offer_price()
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
