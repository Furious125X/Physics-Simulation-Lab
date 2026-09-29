import math
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class DominoScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 550

        self.domino_count = 14
        self.spacing = 38

        self.domino_width = 14
        self.domino_height = 70

        self.start_x = 120
        self.floor_y = 550

        self.dominoes = []

        self.push_strength = 35.0
        self.push_enabled = False

        self.fall_angle = math.pi / 2
        self.angular_speed = 2.5

        self.active_domino = None
        self.fallen_count = 0

        self.create_dominoes()

    def create_dominoes(self):

        for i in range(self.domino_count):

            x = (
                self.start_x
                + i * self.spacing
            )

            y = self.floor_y

            body = Body(
                x,
                y,
                1,
                density=0.01,
                color=self.random_color()
            )

            body.domino_width = self.domino_width
            body.domino_height = self.domino_height
            body.domino_index = i
            body.domino_falling = False
            body.domino_fallen = False

            body.angle = 0.0
            body.angular_velocity = 0.0
            body.velocity = Vector2()

            self.dominoes.append(body)

            self.world.add_body(body)

    def push_first_domino(self):

        if not self.dominoes:
            return

        first = self.dominoes[0]

        first.domino_falling = True
        first.angular_velocity = self.angular_speed

        self.active_domino = 0

    def update_dominoes(self, dt):

        if self.active_domino is None:
            return

        index = self.active_domino

        if index >= len(self.dominoes):
            self.active_domino = None
            return

        body = self.dominoes[index]

        if not body.domino_falling:
            return

        body.angle += (
            body.angular_velocity * dt
        )

        if body.angle >= self.fall_angle:

            body.angle = self.fall_angle
            body.angular_velocity = 0.0
            body.domino_falling = False
            body.domino_fallen = True

            self.fallen_count += 1

            next_index = index + 1

            if next_index < len(self.dominoes):

                next_domino = self.dominoes[next_index]

                next_domino.domino_falling = True
                next_domino.angular_velocity = self.angular_speed

                self.active_domino = next_index

            else:

                self.active_domino = None

    def update(self, dt):

        if self.push_enabled:

            self.push_enabled = False

            self.push_first_domino()

        self.update_dominoes(dt)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                self.push_enabled = True

            elif event.key == pygame.K_z:

                self.push_strength = max(
                    5.0,
                    self.push_strength - 5.0
                )

                self.angular_speed = (
                    1.5
                    + self.push_strength * 0.04
                )

            elif event.key == pygame.K_x:

                self.push_strength = min(
                    100.0,
                    self.push_strength + 5.0
                )

                self.angular_speed = (
                    1.5
                    + self.push_strength * 0.04
                )

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            mouse_position = Vector2(
                mouse_x,
                mouse_y
            )

            self.selected_body = (
                self.find_body_at_position(
                    mouse_position
                )
            )

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

    def draw_domino(self, renderer, body):

        pivot = (
            renderer.camera.world_to_screen(
                body.position
            )
        )

        width = int(
            body.domino_width
            * renderer.camera.zoom
        )

        height = int(
            body.domino_height
            * renderer.camera.zoom
        )

        width = max(
            1,
            width
        )

        height = max(
            1,
            height
        )

        surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            surface,
            body.color,
            (
                0,
                0,
                width,
                height
            )
        )

        rotated_surface = pygame.transform.rotate(
            surface,
            -math.degrees(body.angle)
        )

        center_offset = Vector2(
            0,
            -body.domino_height / 2
        )

        rotated_offset = Vector2(
            center_offset.x * math.cos(body.angle)
            - center_offset.y * math.sin(body.angle),

            center_offset.x * math.sin(body.angle)
            + center_offset.y * math.cos(body.angle)
        )

        screen_center = (
            renderer.camera.world_to_screen(
                body.position
                + rotated_offset
            )
        )

        rect = rotated_surface.get_rect(
            center=(
                int(screen_center.x),
                int(screen_center.y)
            )
        )

        renderer.screen.blit(
            rotated_surface,
            rect
        )

    def draw(self, renderer):

        for body in self.dominoes:

            self.draw_domino(
                renderer,
                body
            )

        floor_start = renderer.camera.world_to_screen(
            Vector2(0, self.floor_y)
        )

        floor_end = renderer.camera.world_to_screen(
            Vector2(800, self.floor_y)
        )

        pygame.draw.line(
            renderer.screen,
            (180, 180, 180),
            (
                int(floor_start.x),
                int(floor_start.y)
            ),
            (
                int(floor_end.x),
                int(floor_end.y)
            ),
            max(
                1,
                int(2 * renderer.camera.zoom)
            )
        )

        text = renderer.font.render(
            (
                f"Dominoes: {len(self.dominoes)}  "
                f"Push: {self.push_strength:.0f}  "
                f"Fallen: {self.fallen_count}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "SPACE: Push  Z/X: Push Strength",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )