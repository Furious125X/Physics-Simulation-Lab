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

        self.segment_count = 12
        self.segment_spacing = 40
        self.segment_radius = 8

        self.start_x = 150
        self.beam_y = 250

        self.beam_bodies = []

        for i in range(self.segment_count):

            body = Body(
                self.start_x + i * self.segment_spacing,
                self.beam_y,
                self.segment_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.2
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.beam_bodies.append(body)

            self.world.add_body(body)


        anchor = Vector2(
            self.start_x,
            self.beam_y
        )

        anchor_constraint = AnchorConstraint(
            self.beam_bodies[0],
            anchor,
            0
        )

        self.world.add_constraint(
            anchor_constraint
        )


        for i in range(
            self.segment_count - 1
        ):

            constraint = DistanceConstraint(
                self.beam_bodies[i],
                self.beam_bodies[i + 1],
                self.segment_spacing,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )


        for i in range(
            self.segment_count - 2
        ):

            constraint = DistanceConstraint(
                self.beam_bodies[i],
                self.beam_bodies[i + 2],
                self.segment_spacing * 2,
                compliance=0.00001
            )

            self.world.add_constraint(
                constraint
            )


        self.load = Body(
            self.start_x
            + (self.segment_count - 1)
            * self.segment_spacing,
            self.beam_y - 60,
            26,
            density=0.01,
            color=self.random_color()
        )

        self.load.linear_damping = 0.2
        self.load.restitution = 0.0
        self.load.static_friction = 0.6
        self.load.dynamic_friction = 0.4

        self.world.add_body(
            self.load
        )

        self.loads = [
            self.load
        ]

        self.load_height = 60

        self.load = Body(
            self.start_x
            + (self.segment_count - 1)
            * self.segment_spacing,

            self.beam_y
            - self.load_height,

            16,
            density=0.01,
            color=self.random_color()
        )


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

            mouse_x, mouse_y = pygame.mouse.get_pos()

            load = Body(
                mouse_x,
                mouse_y,
                16,
                density=0.01,
                color=self.random_color()
            )

            load.linear_damping = 0.2
            load.restitution = 0.0
            load.static_friction = 0.6
            load.dynamic_friction = 0.4

            self.loads.append(load)

            self.world.add_body(load)


    def draw(self, renderer) :
        text = renderer.font.render(
            f"Loads: {len(self.loads)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        for i in range(
            self.segment_count - 1
        ):

            start = renderer.camera.world_to_screen(
                self.beam_bodies[i].position
            )

            end = renderer.camera.world_to_screen(
                self.beam_bodies[i + 1].position
            )

            pygame.draw.line(
                renderer.screen,
                (220, 220, 220),
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