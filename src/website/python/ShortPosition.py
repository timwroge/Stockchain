# Represents a short position, extends Position
# (Right now this feels useless)
import Position

class ShortPosition(Position):
    def __init__(self, stock, shares, currentValue):
        super().__init__(stock, shares, currentValue)
