import math
import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class ElectricFieldScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 550

        self.electric_strength = 30000.0
        self.electric_softening = 25.0
        self.max_electric_force = 250.0

        self.electric_enabled = True

        self.sources = []
        self.test_charges = []

        self.create_source(
            400,
            300,
            1
        )

        self.create_source(
            600,
            300,
            -1
        )

        self.create_test_charge(
            250,
            250,
            1
        )

        self.create_test_charge(
            250,
            400,
            -1
        )

        self.create_test_charge(
            500,
            180,
            1
        )

        self.create_test_charge(
            500,
            450,
            -1
        )

    def create_source(
        self,
        x,
        y,
        charge
    ):

        body = Body(
            x,
            y,
            18,
            density=0.005,
            color=self.get_charge_color(
                charge,
                True
            ),
            is_static=True
        )

        body.electric_charge = charge
        body.is_source = True

        self.sources.append(body)
        self.world.add_body(body)

    def create_test_charge(
        self,
        x,
        y,
        charge
    ):

        body = Body(
            x,
            y,
            10,
            density=0.005,
            color=self.get_charge_color(
                charge,
                False
            )
        )

        body.electric_charge = charge
        body.is_source = False

        body.linear_damping = 0.4
        body.restitution = 0.3
        body.static_friction = 0.4
        body.dynamic_friction = 0.2

        self.test_charges.append(body)
        self.world.add_body(body)

    def get_charge_color(
        self,
        charge,
        source
    ):

        if charge > 0:

            if source:
                return (255, 70, 70)

            return (255, 150, 150)

        if source:
            return (70, 100, 255)

        return (140, 170, 255)

    def apply_electric_forces(self):

        if not self.electric_enabled:
            return

        for charge_body in self.test_charges:

            force = Vector2()

            for source in self.sources:

                difference = (
                    charge_body.position
                    - source.position
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
                    + self.electric_softening
                    * self.electric_softening
                )

                force_magnitude = (
                    self.electric_strength
                    * abs(
                        source.electric_charge
                        * charge_body.electric_charge
                    )
                    / effective_distance_squared
                )

                if (
                    source.electric_charge
                    == charge_body.electric_charge
                ):

                    pair_force = (
                        direction
                        * force_magnitude
                    )

                else:

                    pair_force = (
                        direction
                        * -force_magnitude
                    )

                force += pair_force

            force_length = force.length()

            if force_length > self.max_electric_force:

                force = (
                    force.normalize()
                    * self.max_electric_force
                )

            charge_body.apply_force(force)

    def update(self, dt):

        self.apply_electric_forces()

        super().update(dt)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                self.electric_enabled = (
                    not self.electric_enabled
                )

            elif event.key == pygame.K_z:

                self.electric_strength = max(
                    0.0,
                    self.electric_strength - 3000.0
                )

            elif event.key == pygame.K_x:

                self.electric_strength = min(
                    60000.0,
                    self.electric_strength + 3000.0
                )

            elif event.key == pygame.K_v:

                if self.selected_body is not None:

                    if (
                        hasattr(
                            self.selected_body,
                            "electric_charge"
                        )
                        and not self.selected_body.is_source
                    ):

                        self.selected_body.electric_charge *= -1

                        self.selected_body.color = (
                            self.get_charge_color(
                                self.selected_body.electric_charge,
                                False
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
            if self.electric_enabled
            else "OFF"
        )

        selected_charge = "None"

        if self.selected_body is not None:

            if (
                hasattr(
                    self.selected_body,
                    "electric_charge"
                )
            ):

                if self.selected_body.electric_charge > 0:
                    selected_charge = "+"

                else:
                    selected_charge = "-"

        text = renderer.font.render(
            (
                f"Electric Field: {status}  "
                f"Strength: {self.electric_strength:.0f}  "
                f"Selected: {selected_charge}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "SPACE: Toggle  Z/X: Strength  V: Flip Selected Charge",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )

        legend = renderer.font.render(
            "Red: Positive  Blue: Negative",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            legend,
            (10, 160)
        )