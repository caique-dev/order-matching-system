from MatchingEngine import MatchingEngine

engine = MatchingEngine()
engine.manual_input_handler('create order limit sell 1 1, create order limit sell 2 2, pause, create order market buy 4')
# engine.manual_input_handler()
# engine.manual_input_handler('create order limit sell 200 10, create order limit buy 100 20, create order pegged bid buy 10, create order pegged offer sell 20')