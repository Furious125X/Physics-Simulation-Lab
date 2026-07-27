import pygame
import math
from physics.constraints import AnchorConstraint, DistanceConstraint


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def draw_body(self, body):
        pygame.draw.circle(
            self.screen,
            body.color,
            (int(body.position.x), int(body.position.y)),
            body.radius
        )
        end_x = body.position.x + math.cos(body.angle) * body.radius
        end_y = body.position.y + math.sin(body.angle) * body.radius
        pygame.draw.line(
                    self.screen,
                    (255, 255, 255),
                    (int(body.position.x), int(body.position.y)),
                    (end_x, end_y)
                )

    def draw_spring(self, spring):
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (int(spring.body1.position.x), int(spring.body1.position.y)),
            (int(spring.body2.position.x), int(spring.body2.position.y)),
            spring.width
        )

    def draw_constraint(self, constraint):

        if isinstance(constraint, AnchorConstraint):

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (int(constraint.body.position.x), int(constraint.body.position.y)),
                (int(constraint.anchor.x), int(constraint.anchor.y)),
                2
            )

        elif isinstance(constraint, DistanceConstraint):

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (int(constraint.body1.position.x), int(constraint.body1.position.y)),
                (int(constraint.body2.position.x), int(constraint.body2.position.y)),
                2
            )