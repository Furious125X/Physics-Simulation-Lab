import math
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene

class SuspensionBridgeScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 700


        self.sections = 12
        self.spacing = 40

        self.start_x = 160

        self.cable_y = 220
        self.deck_y = 380

        self.cable_sag = 100

        self.node_radius = 7

        self.cable_bodies = []

        for i in range(self.sections + 1):

            x = (
                self.start_x
                + i * self.spacing
            )

            normalized = (
                i / self.sections
            )

            sag = (
                self.cable_sag
                * math.sin(math.pi * normalized)
            )

            y = self.cable_y + sag

            body = Body(
                x,
                y,
                self.node_radius,
                color=self.random_color()
            )

            body.linear_damping = 0.25
            body.restitution = 0.0
            body.static_friction = 0.4
            body.dynamic_friction = 0.3

            self.cable_bodies.append(body)

            self.world.add_body(body)


        left_anchor = Vector2(
            self.start_x,
            self.cable_y
        )

        left_constraint = AnchorConstraint(
            self.cable_bodies[0],
            left_anchor,
            0
        )

        self.world.add_constraint(
            left_constraint
        )


        right_anchor = Vector2(
            self.start_x
            + self.sections * self.spacing,
            self.cable_y
        )

        right_constraint = AnchorConstraint(
            self.cable_bodies[-1],
            right_anchor,
            0
        )

        self.world.add_constraint(
            right_constraint
        )


        for i in range(self.sections):

            constraint = DistanceConstraint(
                self.cable_bodies[i],
                self.cable_bodies[i + 1],
                self.spacing,
                compliance=0.00001
            )

            self.world.add_constraint(
                constraint
            )

        self.deck_bodies = []

        for i in range(self.sections + 1):

            body = Body(
                self.start_x + i * self.spacing,
                self.deck_y,
                self.node_radius + 2,
                color=self.random_color()
            )

            body.linear_damping = 0.2
            body.restitution = 0.0
            body.static_friction = 0.6
            body.dynamic_friction = 0.4

            self.deck_bodies.append(body)

            self.world.add_body(body)


        for i in range(self.sections):

            constraint = DistanceConstraint(
                self.deck_bodies[i],
                self.deck_bodies[i + 1],
                self.spacing,
                compliance=0.000001
            )

            self.world.add_constraint(
                constraint
            )


        for i in range(self.sections - 1):

            constraint = DistanceConstraint(
                self.deck_bodies[i],
                self.deck_bodies[i + 2],
                self.spacing * 2,
                compliance=0.00001
            )

            self.world.add_constraint(
                constraint
            )

        left_deck_anchor = Vector2(
            self.start_x,
            self.deck_y
        )

        left_deck_constraint = AnchorConstraint(
            self.deck_bodies[0],
            left_deck_anchor,
            0
        )

        self.world.add_constraint(
            left_deck_constraint
        )

        right_deck_anchor = Vector2(
            self.start_x
            + self.sections * self.spacing,
            self.deck_y
        )

        right_deck_constraint = AnchorConstraint(
            self.deck_bodies[-1],
            right_deck_anchor,
            0
        )

        self.world.add_constraint(
            right_deck_constraint
        )

        self.hangers = []

        for i in range(1, self.sections):

            cable_body = self.cable_bodies[i]
            deck_body = self.deck_bodies[i]

            distance = (
                deck_body.position
                - cable_body.position
            ).length()

            constraint = DistanceConstraint(
                cable_body,
                deck_body,
                distance,
                compliance=0.00001
            )

            self.hangers.append(
                constraint
            )

            self.world.add_constraint(
                constraint
            )

        self.loads = []

        load_positions = [
            self.start_x + 4 * self.spacing,
            self.start_x + 5 * self.spacing,
            self.start_x + 6 * self.spacing,
            self.start_x + 7 * self.spacing,
            self.start_x + 8 * self.spacing
        ]

        for x in load_positions:

            load = Body(
                x,
                self.deck_y - 60,
                14,
                density=0.01,
                color=self.random_color()
            )

            load.linear_damping = 0.2
            load.restitution = 0.0
            load.static_friction = 0.6
            load.dynamic_friction = 0.4

            self.loads.append(load)

            self.world.add_body(load)


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
                14,
                density=0.01,
                color=self.random_color()
            )

            load.linear_damping = 0.2
            load.restitution = 0.0
            load.static_friction = 0.6
            load.dynamic_friction = 0.4

            self.loads.append(load)

            self.world.add_body(load)


    def draw(self,renderer) :

        text = renderer.font.render(
            f"Loads: {len(self.loads)}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        for i in range(self.sections):

            start = renderer.camera.world_to_screen(
                self.cable_bodies[i].position
            )

            end = renderer.camera.world_to_screen(
                self.cable_bodies[i + 1].position
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
                4
            )

        for i in range(self.sections):

            start = renderer.camera.world_to_screen(
                self.deck_bodies[i].position
            )

            end = renderer.camera.world_to_screen(
                self.deck_bodies[i + 1].position
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

        for constraint in self.hangers:

            start = renderer.camera.world_to_screen(
                constraint.body1.position
            )

            end = renderer.camera.world_to_screen(
                constraint.body2.position
            )

            pygame.draw.line(
                renderer.screen,
                (180, 180, 180),
                (
                    int(start.x),
                    int(start.y)
                ),
                (
                    int(end.x),
                    int(end.y)
                ),
                2
            )

        left = renderer.camera.world_to_screen(
            Vector2(
                self.start_x,
                self.deck_y
            )
        )

        right = renderer.camera.world_to_screen(
            Vector2(
                self.start_x
                + self.sections * self.spacing,
                self.deck_y
            )
        )