import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class MagnetismScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 550

        self.magnetic_strength = 25000.0
        self.magnetic_softening = 20.0
        self.max_magnetic_force = 300.0

        self.magnets = []

        self.magnetic_enabled = True

        self.create_magnet(
            250,
            250,
            1
        )

        self.create_magnet(
            550,
            250,
            -1
        )

        self.create_magnet(
            250,
            400,
            -1
        )

        self.create_magnet(
            550,
            400,
            1
        )

    def create_magnet(
        self,
        x,
        y,
        polarity
    ):

        body = Body(
            x,
            y,
            14,
            density=0.005,
            color=self.get_magnet_color(
                polarity
            )
        )

        body.linear_damping = 0.4
        body.restitution = 0.4
        body.static_friction = 0.5
        body.dynamic_friction = 0.3

        body.polarity = polarity

        self.magnets.append(body)
        self.world.add_body(body)

    def get_magnet_color(self, polarity):

        if polarity > 0:
            return (255, 80, 80)

        return (80, 120, 255)

    def apply_magnetic_forces(self):

        if not self.magnetic_enabled:
            return

        magnet_count = len(self.magnets)

        for i in range(magnet_count):

            body1 = self.magnets[i]

            for j in range(i + 1, magnet_count):

                body2 = self.magnets[j]

                difference = (
                    body2.position
                    - body1.position
                )

                distance_squared = (
                    difference.length_squared()
                )

                if distance_squared == 0:
                    continue

                distance = (
                    distance_squared ** 0.5
                )

                direction = (
                    difference
                    / distance
                )

                effective_distance_squared = (
                    distance_squared
                    + self.magnetic_softening
                    * self.magnetic_softening
                )

                acceleration = (
                    self.magnetic_strength
                    / effective_distance_squared
                )

                force_magnitude = (
                    acceleration
                    * body1.mass
                    * self.world.substeps
                )

                if body1.polarity == body2.polarity:

                    force = (
                        direction
                        * -force_magnitude
                    )

                else:

                    force = (
                        direction
                        * force_magnitude
                    )

                force_length = force.length()

                if force_length > self.max_magnetic_force:

                    force = (
                        force.normalize()
                        * self.max_magnetic_force
                    )

                body1.apply_force(force)
                body2.apply_force(-force)

    def update(self, dt):

        self.apply_magnetic_forces()

        super().update(dt)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                self.magnetic_enabled = (
                    not self.magnetic_enabled
                )

            elif event.key == pygame.K_z:

                self.magnetic_strength = max(
                    0.0,
                    self.magnetic_strength - 2500.0
                )

            elif event.key == pygame.K_x:

                self.magnetic_strength = min(
                    50000.0,
                    self.magnetic_strength + 2500.0
                )

            elif event.key == pygame.K_v:

                if self.selected_body is not None:

                    if self.selected_body in self.magnets:

                        self.selected_body.polarity *= -1

                        self.selected_body.color = (
                            self.get_magnet_color(
                                self.selected_body.polarity
                            )
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

    def draw(self, renderer):

        self.world.draw(renderer)

        status = (
            "ON"
            if self.magnetic_enabled
            else "OFF"
        )

        selected_polarity = "None"

        if self.selected_body is not None:

            if self.selected_body in self.magnets:

                if self.selected_body.polarity > 0:
                    selected_polarity = "N"
                else:
                    selected_polarity = "S"

        text = renderer.font.render(
            (
                f"Magnetism: {status}  "
                f"Strength: {self.magnetic_strength:.0f}  "
                f"Selected: {selected_polarity}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "SPACE: Toggle  Z/X: Strength  V: Flip Selected Pole",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )

        legend = renderer.font.render(
            "Red: N  Blue: S",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            legend,
            (10, 160)
        )