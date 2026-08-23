import random
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene

class ClothScene(Scene):

    def __init__(self):
        super().__init__()

        self.world.enable_collisions = False
        self.world.constraint_iterations = 6
        self.world.substeps = 2

        rows = 12
        cols = 18

        spacing = 25
        radius = 5

        start_x = 180
        start_y = 40

        grid = []

        for row in range(rows):
            current_row = []

            for col in range(cols):
                x = start_x + col * spacing
                y = start_y + row * spacing

                body = Body(x, y, radius, color=self.random_color())
                self.world.add_body(body)
                current_row.append(body)

            grid.append(current_row)

        for body in grid[0]:
            anchor = Vector2(body.position.x, body.position.y)
            constraint = AnchorConstraint(body, anchor, 0)
            self.world.add_constraint(constraint)

        for row in range(rows):
            for col in range(cols - 1):
                constraint = DistanceConstraint(grid[row][col], grid[row][col + 1], spacing)
                self.world.add_constraint(constraint)

        for row in range(rows - 1):
            for col in range(cols):
                constraint = DistanceConstraint(grid[row][col], grid[row + 1][col], spacing)
                self.world.add_constraint(constraint)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)
            self.selected_body = self.find_body_at_position(mouse_position)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected_body = None

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)