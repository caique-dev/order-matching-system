class Order:
    def __init__(self, vec):
        self.id = None
        self.type = vec[0]
        self.side = vec[1]
        
        if (self.type == "limit"):
            self.price = vec[2]
            self.qty = vec[3]
        else:
            self.qty = vec[2]

        # verifications
        if (self.qty == 0 or self.price == 0):
            pass
            # todo implementar tratamento

        return
    
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
    
    # def __repr__(self):
    #     self.__str__()
        

class OrderBook:
    def __init__(self):
        self.buy_side_vec = []
        self.buy_side_index = 0

        self.sell_side_vec = []
        self.sell_side_index = 0

    def __str__(self):
        _str = 'Buy Side: \n'
        for order in self.buy_side_vec:
            _str += str(order) + '\n'

        _str += 'Sell Side: \n'
        for order in self.sell_side_vec:
            _str += str(order) + '\n'
        
        return _str

    def __repr__(self):
        return self.orders_num

class MatchingMachine:
    def __init__(self, book: OrderBook):
        self.book = book

    def add_order(self, order):
        # create the object
        obj_order = Order(order)

        # adding to the book
        if (obj_order.side == 'buy'):
            self.book.buy_side_vec.append(obj_order)
            # filling id
            obj_order.id = self.book.buy_side_index
            self.book.buy_side_index += 1
        else: 
            self.book.sell_side_vec.append(obj_order)
            # filling id
            obj_order.id = self.book.sell_side_index
            self.book.sell_side_index += 1


    def execute_order():
        pass

primary_book = OrderBook()
machine = MatchingMachine(primary_book)

current_order = 'limit buy 10 100'.split()
machine.add_order(current_order)
print(current_order)

current_order = 'limit sell 20 100'.split()
machine.add_order(current_order)
print(current_order)

current_order = 'limit sell 20 200'.split()
machine.add_order(current_order)
print(current_order)

print(primary_book)