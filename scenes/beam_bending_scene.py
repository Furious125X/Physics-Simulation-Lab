import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene


class BeamBendingScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700

        self.segment_count = 13
        self.segment_spacing = 40
        self.segment_radius = 10

        self.start_x = 140
        self.beam_y = 250

        self.warning_deflection = 25
        self.failure_deflection = 50

        self.beam_bodies = []

        for i in range(self.segment_count):

            body = Body(
                self.start_x + i * self.segment_spacing,
                self.beam_y,
                self.segment_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.8
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.beam_bodies.append(body)
            self.world.add_body(body)

        self.original_positions = [
            body.position.copy()
            for body in self.beam_bodies
        ]

        left_anchor = AnchorConstraint(
            self.beam_bodies[0],
            Vector2(
                self.start_x,
                self.beam_y
            ),
            0
        )

        right_anchor = AnchorConstraint(
            self.beam_bodies[-1],
            Vector2(
                self.start_x
                + (self.segment_count - 1)
                * self.segment_spacing,
                self.beam_y
            ),
            0
        )

        self.world.add_constraint(left_anchor)
        self.world.add_constraint(right_anchor)

        for i in range(self.segment_count - 1):

            constraint = DistanceConstraint(
                self.beam_bodies[i],
                self.beam_bodies[i + 1],
                self.segment_spacing,
                compliance=0.0
            )

            self.world.add_constraint(constraint)

        for i in range(self.segment_count - 2):

            constraint = DistanceConstraint(
                self.beam_bodies[i],
                self.beam_bodies[i + 2],
                self.segment_spacing * 2,
                compliance=0.00005
            )

            self.world.add_constraint(constraint)

        self.loads = []

        self.add_load()

    def add_load(self):

        center_x = (
            self.start_x
            + (self.segment_count - 1)
            * self.segment_spacing
            * 0.5
        )

        load = Body(
            center_x,
            self.beam_y - 135,
            18,
            density=0.01,
            color=self.random_color()
        )

        load.linear_damping = 0.8
        load.restitution = 0.0
        load.static_friction = 0.6
        load.dynamic_friction = 0.4

        self.loads.append(load)
        self.world.add_body(load)

    def get_max_deflection(self):

        max_deflection = 0.0

        for body, original in zip(
            self.beam_bodies,
            self.original_positions
        ):

            deflection = (
                body.position - original
            ).length()

            max_deflection = max(
                max_deflection,
                deflection
            )

        return max_deflection

    def handle_event(self, event):

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

        elif event.type == pygame.MOUSEWHEEL:

            self.add_load()

    def draw(self, renderer):

        self.world.draw(renderer)

        max_deflection = self.get_max_deflection()

        if max_deflection >= self.failure_deflection:
            beam_color = (255, 80, 80)
            status = "FAILURE"

        elif max_deflection >= self.warning_deflection:
            beam_color = (255, 200, 80)
            status = "WARNING"

        else:
            beam_color = (220, 220, 220)
            status = "STABLE"

        total_mass = sum(
            load.mass
            for load in self.loads
        )

        text = renderer.font.render(
            f"Loads: {len(self.loads)}   "
            f"Mass: {total_mass:.2f}   "
            f"Deflection: {max_deflection:.1f}px   "
            f"{status}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        for i in range(self.segment_count - 1):

            start = renderer.camera.world_to_screen(
                self.beam_bodies[i].position
            )

            end = renderer.camera.world_to_screen(
                self.beam_bodies[i + 1].position
            )

            pygame.draw.line(
                renderer.screen,
                beam_color,
                (
                    int(start.x),
                    int(start.y)
                ),
                (
                    int(end.x),
                    int(end.y)
                ),
                6
            )