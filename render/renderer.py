import pygame
import math

from physics.constraints import AnchorConstraint, DistanceConstraint
from physics.vector import Vector2
from render.camera import Camera


class Renderer:

    def __init__(self, screen):
        self.screen = screen
        self.camera = Camera()
        self.font = pygame.font.SysFont(None, 18)

    def draw_body(self, body):
        screen_position = self.camera.world_to_screen(body.position)

        pygame.draw.circle(
            self.screen,
            body.color,
            (int(screen_position.x), int(screen_position.y)),
            body.radius
        )

        end_x = int(
            screen_position.x +
            math.cos(body.angle) * body.radius
        )
        end_y = int(
            screen_position.y +
            math.sin(body.angle) * body.radius
        )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (int(screen_position.x), int(screen_position.y)),
            (end_x, end_y),
            2
        )

    def draw_spring(self, spring):
        screen_position1 = self.camera.world_to_screen(
            spring.body1.position
        )
        screen_position2 = self.camera.world_to_screen(
            spring.body2.position
        )

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (int(screen_position1.x), int(screen_position1.y)),
            (int(screen_position2.x), int(screen_position2.y)),
            spring.width
        )

    def draw_constraint(self, constraint):
        if isinstance(constraint, AnchorConstraint):
            body_position = self.camera.world_to_screen(
                constraint.body.position
            )
            anchor_position = self.camera.world_to_screen(
                constraint.anchor
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (int(body_position.x), int(body_position.y)),
                (int(anchor_position.x), int(anchor_position.y)),
                2
            )

        elif isinstance(constraint, DistanceConstraint):
            body1_position = self.camera.world_to_screen(
                constraint.body1.position
            )
            body2_position = self.camera.world_to_screen(
                constraint.body2.position
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (int(body1_position.x), int(body1_position.y)),
                (int(body2_position.x), int(body2_position.y)),
                2
            )

    def draw_body_debug(self, body):
        screen_position = self.camera.world_to_screen(body.position)

        if body.is_static:
            color = (255, 120, 120)
        elif body.sleeping:
            color = (80, 160, 255)
        else:
            color = (255, 180, 80)

        pygame.draw.circle(
            self.screen,
            color,
            (int(screen_position.x), int(screen_position.y)),
            body.radius,
            1
        )

        label = self.font.render(
            str(body.id),
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            label,
            (
                int(screen_position.x) + body.radius + 2,
                int(screen_position.y) - body.radius - 2
            )
        )

    def draw_spring_debug(self, spring):
        screen_position1 = self.camera.world_to_screen(
            spring.body1.position
        )
        screen_position2 = self.camera.world_to_screen(
            spring.body2.position
        )

        pygame.draw.line(
            self.screen,
            (255, 100, 100),
            (int(screen_position1.x), int(screen_position1.y)),
            (int(screen_position2.x), int(screen_position2.y)),
            1
        )

    def draw_constraint_debug(self, constraint):
        if hasattr(constraint, "body1") and hasattr(constraint, "body2"):
            body1_position = self.camera.world_to_screen(
                constraint.body1.position
            )
            body2_position = self.camera.world_to_screen(
                constraint.body2.position
            )

            start = (
                int(body1_position.x),
                int(body1_position.y)
            )
            end = (
                int(body2_position.x),
                int(body2_position.y)
            )

            pygame.draw.line(
                self.screen,
                (100, 100, 255),
                start,
                end,
                1
            )

            mid_x = (start[0] + end[0]) // 2
            mid_y = (start[1] + end[1]) // 2

            label = self.font.render(
                f"D {constraint.length:.1f}",
                True,
                (200, 200, 255)
            )

            self.screen.blit(
                label,
                (mid_x + 4, mid_y + 4)
            )

        elif hasattr(constraint, "body") and hasattr(constraint, "anchor"):
            body_position = self.camera.world_to_screen(
                constraint.body.position
            )
            anchor_position = self.camera.world_to_screen(
                constraint.anchor
            )

            body_pos = (
                int(body_position.x),
                int(body_position.y)
            )
            anchor_pos = (
                int(anchor_position.x),
                int(anchor_position.y)
            )

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

            label = self.font.render(
                f"A {constraint.length:.1f}",
                True,
                (255, 220, 180)
            )

            self.screen.blit(
                label,
                (mid_x + 4, mid_y + 4)
            )

    def draw_spatial_grid_debug(self, grid):
        cell_size = grid.cell_size

        for (cell_x, cell_y), bodies in grid.cells.items():
            world_position = Vector2(
                cell_x * cell_size,
                cell_y * cell_size
            )

            screen_position = self.camera.world_to_screen(
                world_position
            )

            x = int(screen_position.x)
            y = int(screen_position.y)

            rect = pygame.Rect(
                x,
                y,
                cell_size,
                cell_size
            )

            pygame.draw.rect(
                self.screen,
                (120, 120, 120),
                rect,
                1
            )

            if bodies:
                label = self.font.render(
                    str(len(bodies)),
                    True,
                    (180, 180, 180)
                )

                self.screen.blit(
                    label,
                    (x + 2, y + 2)
                )

    def draw_collision_normal_debug(self, point, normal, color):
        screen_point = self.camera.world_to_screen(point)

        start = (
            int(screen_point.x),
            int(screen_point.y)
        )

        end = (
            int(screen_point.x + normal.x * 25),
            int(screen_point.y + normal.y * 25)
        )

        pygame.draw.line(
            self.screen,
            color,
            start,
            end,
            2
        )

        pygame.draw.circle(
            self.screen,
            color,
            start,
            3
        )

    def draw_velocity_vector_debug(self, body):
        screen_position = self.camera.world_to_screen(
            body.position
        )

        start = (
            int(screen_position.x),
            int(screen_position.y)
        )

        scale = 0.08

        end = (
            int(screen_position.x + body.velocity.x * scale),
            int(screen_position.y + body.velocity.y * scale)
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
        screen_position = self.camera.world_to_screen(
            body.position
        )

        start = (
            int(screen_position.x),
            int(screen_position.y)
        )

        scale = 0.02

        end = (
            int(screen_position.x + body.debug_force.x * scale),
            int(screen_position.y + body.debug_force.y * scale)
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

    def draw_bounding_box_debug(self, body):
        left, top, right, bottom = body.get_aabb()

        top_left = self.camera.world_to_screen(
            Vector2(left, top)
        )

        bottom_right = self.camera.world_to_screen(
            Vector2(right, bottom)
        )

        rect = pygame.Rect(
            int(top_left.x),
            int(top_left.y),
            int(bottom_right.x - top_left.x),
            int(bottom_right.y - top_left.y)
        )

        pygame.draw.rect(
            self.screen,
            (255, 0, 255),
            rect,
            1
        )

    def draw_sleeping_debug(self, body):
        screen_position = self.camera.world_to_screen(
            body.position
        )

        if body.sleeping:
            color = (80, 160, 255)
        else:
            color = (255, 180, 80)

        pygame.draw.circle(
            self.screen,
            color,
            (int(screen_position.x), int(screen_position.y)),
            body.radius,
            2
        )