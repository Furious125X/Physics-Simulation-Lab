import pygame
import math

from physics.constraints import AnchorConstraint, DistanceConstraint


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 18)

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
        color = (255, 255, 0) if not body.is_static else (255, 120, 120)

        pygame.draw.circle(
            self.screen,
            color,
            (int(body.position.x), int(body.position.y)),
            body.radius,
            1
        )

        label = self.font.render(str(body.id), True, (255, 255, 255))
        self.screen.blit(
            label,
            (int(body.position.x) + body.radius + 2, int(body.position.y) - body.radius - 2)
        )

    def draw_spring_debug(self, spring):
        pygame.draw.line(
            self.screen,
            (255, 100, 100),
            (int(spring.body1.position.x), int(spring.body1.position.y)),
            (int(spring.body2.position.x), int(spring.body2.position.y)), 1)


    def draw_constraint_debug(self, constraint):
        if hasattr(constraint, "body1") and hasattr(constraint, "body2"):
            start = (int(constraint.body1.position.x), int(constraint.body1.position.y))
            end = (int(constraint.body2.position.x), int(constraint.body2.position.y))

            pygame.draw.line(
                self.screen,
                (100, 100, 255),
                start,
                end,
                1
            )

            mid_x = (start[0] + end[0]) // 2
            mid_y = (start[1] + end[1]) // 2

            label = self.font.render(f"D {constraint.length:.1f}", True, (200, 200, 255))
            self.screen.blit(label, (mid_x + 4, mid_y + 4))

        elif hasattr(constraint, "body") and hasattr(constraint, "anchor"):
            body_pos = (int(constraint.body.position.x), int(constraint.body.position.y))
            anchor_pos = (int(constraint.anchor.x), int(constraint.anchor.y))

            pygame.draw.line(
                self.screen,
                (255, 160, 100),
                body_pos,
                anchor_pos,
                1
            )

            pygame.draw.circle(
                self.screen,
                (255, 200, 100),
                anchor_pos,
                4
            )

            mid_x = (body_pos[0] + anchor_pos[0]) // 2
            mid_y = (body_pos[1] + anchor_pos[1]) // 2

            label = self.font.render(f"A {constraint.length:.1f}", True, (255, 220, 180))
            self.screen.blit(label, (mid_x + 4, mid_y + 4))


    def draw_spatial_grid_debug(self, grid):
        cell_size = grid.cell_size

        for (cell_x, cell_y), bodies in grid.cells.items():
            x = cell_x * cell_size
            y = cell_y * cell_size

            rect = pygame.Rect(x, y, cell_size, cell_size)

            pygame.draw.rect(
                self.screen,
                (120, 120, 120),
                rect,
                1
            )

            if bodies:
                label = self.font.render(str(len(bodies)), True, (180, 180, 180))
                self.screen.blit(label, (x + 2, y + 2))


    def draw_collision_normal_debug(self, point, normal, color):
        start = (int(point.x), int(point.y))
        end = (
            int(point.x + normal.x * 25),
            int(point.y + normal.y * 25)
        )

        pygame.draw.line(self.screen, color, start, end, 2)

        pygame.draw.circle(self.screen, color, start, 3)


    def draw_velocity_vector_debug(self, body):
        start = (int(body.position.x), int(body.position.y))

        scale = 0.08
        end = (
            int(body.position.x + body.velocity.x * scale),
            int(body.position.y + body.velocity.y * scale)
        )

        pygame.draw.line(
            self.screen,
            (0, 255, 0),
            start,
            end,
            2
        )

        pygame.draw.circle(
            self.screen,
            (0, 255, 0),
            end,
            3
        )


    def draw_force_vector_debug(self, body):
        start = (
            int(body.position.x),
            int(body.position.y)
        )

        scale = 0.02

        end = (
            int(body.position.x + body.debug_force.x * scale),
            int(body.position.y + body.debug_force.y * scale)
        )

        pygame.draw.line(
            self.screen,
            (255, 140, 0),
            start,
            end,
            2
        )

        pygame.draw.circle(
            self.screen,
            (255, 140, 0),
            end,
            3
        )