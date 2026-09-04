import random
import pygame
import math

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
        self.world.constraint_iterations = 12
        self.world.substeps = 2

        rows = 12
        cols = 18

        spacing = 25
        radius = 5

        shear_stiffness = 1.0
        bending_stiffness = 1.0

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

        for row in range(rows - 1):

            for col in range(cols - 1):

                top_left = grid[row][col]
                top_right = grid[row][col + 1]

                bottom_left = grid[row + 1][col]
                bottom_right = grid[row + 1][col + 1]

                diagonal_length = spacing * math.sqrt(2)

                constraint_1 = DistanceConstraint(top_left, bottom_right, diagonal_length)

                constraint_2 = DistanceConstraint(top_right, bottom_left, diagonal_length)

                self.world.add_constraint(constraint_1)
                self.world.add_constraint(constraint_2)

        for row in range(rows):

            for col in range(cols - 2):

                constraint = DistanceConstraint(
                    grid[row][col],
                    grid[row][col + 2],
                    spacing * 2
                )

                self.world.add_constraint(
                    constraint
                )

        for row in range(rows - 2):

            for col in range(cols):

                constraint = DistanceConstraint(
                    grid[row][col],
                    grid[row + 2][col],
                    spacing * 2
                )

                self.world.add_constraint(
                    constraint
                )


        for row in range(rows - 2):

            for col in range(cols - 2):

                diagonal_length = (
                    spacing
                    * 2
                    * math.sqrt(2)
                )

                constraint_1 = DistanceConstraint(
                    grid[row][col],
                    grid[row + 2][col + 2],
                    diagonal_length
                )

                constraint_2 = DistanceConstraint(
                    grid[row][col + 2],
                    grid[row + 2][col],
                    diagonal_length
                )

                self.world.add_constraint(
                    constraint_1
                )

                self.world.add_constraint(
                    constraint_2
                )

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