class Stop:
    def __init__(self, x, y, stop_name, stop_id):
        self.x = x
        self.y = y
        self.stop_name = stop_name
        self.settled = False
        self.stop_id = stop_id

    def __eq__(self, other):
        if not isinstance(other, Stop):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        if self.x < other.x:
            return True
        else:
            return self.y < other.y

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return str(self.x) + "," + str(self.y)

    def settle(self):
        self.settled = True

    def is_settled(self):
        return self.settled

    def get_coods(self):
        return self.x, self.y

    def set_coods(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_stop_name(self):
        return self.stop_name

    def get_id(self):
        return self.stop_id
