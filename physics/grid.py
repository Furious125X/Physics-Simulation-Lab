class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}

    def clear(self):
        self.cells = {}

    def insert(self, body):
        cell_x = int(body.position.x // self.cell_size)
        cell_y = int(body.position.y // self.cell_size)

        key = (cell_x, cell_y)

        if key not in self.cells:
            self.cells[key] = []

        self.cells[key].append(body)

    def build(self, bodies):
        self.clear()

        for body in bodies:
            self.insert(body)