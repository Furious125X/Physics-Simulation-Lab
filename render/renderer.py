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

        end_x = int(body.position.x + math.cos(body.angle) * body.radius)
        end_y = int(body.position.y + math.sin(body.angle) * body.radius)

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (int(body.position.x), int(body.position.y)),
            (end_x, end_y),
            2
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


    def draw_body_debug(self, body):
        pygame.draw.circle(self.screen, (255, 255, 0), (int(body.position.x), int(body.position.y)), body.radius, 1)

        end_x = int(body.position.x + body.velocity.x * 0.05)
        end_y = int(body.position.y + body.velocity.y * 0.05)

        pygame.draw.line(self.screen, (0, 255, 0), (int(body.position.x), int(body.position.y)), (end_x, end_y), 1)


    def draw_spring_debug(self, spring):
        pygame.draw.line(
            self.screen,
            (255, 100, 100),
            (int(spring.body1.position.x), int(spring.body1.position.y)),
            (int(spring.body2.position.x), int(spring.body2.position.y)), 1)


    def draw_constraint_debug(self, constraint):
        if hasattr(constraint, "body1") and hasattr(constraint, "body2"):
            pygame.draw.line(
                self.screen,
                (100, 100, 255),
                (int(constraint.body1.position.x), int(constraint.body1.position.y)),
                (int(constraint.body2.position.x), int(constraint.body2.position.y)),
                1
            )
        elif hasattr(constraint, "body") and hasattr(constraint, "anchor"):
            pygame.draw.line(
                self.screen,
                (100, 100, 255),
                (int(constraint.body.position.x), int(constraint.body.position.y)),
                (int(constraint.anchor.x), int(constraint.anchor.y)),
                1
            )