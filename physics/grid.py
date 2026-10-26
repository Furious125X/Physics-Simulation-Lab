class SpatialGrid:

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.cells = {}

        # Records which cells each body was inserted into.
        self.body_cells = {}

    def clear(self):
        self.cells = {}
        self.body_cells = {}

    def get_body_cells(self, body):

        left, top, right, bottom = body.get_aabb()

        min_cell_x = int(left // self.cell_size)
        max_cell_x = int(right // self.cell_size)

        min_cell_y = int(top // self.cell_size)
        max_cell_y = int(bottom // self.cell_size)

        occupied_cells = []

        for cell_x in range(
            min_cell_x,
            max_cell_x + 1
        ):

            for cell_y in range(
                min_cell_y,
                max_cell_y + 1
            ):

                occupied_cells.append(
                    (cell_x, cell_y)
                )

        return occupied_cells

    def insert(self, body):

        occupied_cells = self.get_body_cells(body)

        self.body_cells[body] = occupied_cells

        for key in occupied_cells:

            if key not in self.cells:
                self.cells[key] = []

            self.cells[key].append(body)

    def remove(self, body):

        occupied_cells = self.body_cells.pop(
            body,
            []
        )

        for key in occupied_cells:

            cell_bodies = self.cells.get(key)

            if cell_bodies is None:
                continue

            if body in cell_bodies:
                cell_bodies.remove(body)

            if not cell_bodies:
                del self.cells[key]

    def build(self, bodies):

        self.clear()

        for body in bodies:
            self.insert(body)

    def get_occupied_cells(self, body):

        return self.body_cells.get(body, [])

    def get_neighbor_cells(self, cell_x, cell_y):

        neighbors = []

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):

                key = (
                    cell_x + dx,
                    cell_y + dy
                )

                if key in self.cells:
                    neighbors.extend(self.cells[key])

        return neighbors