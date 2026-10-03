import pygame

from physics.body import Body
from physics.constraints import DistanceConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene


class RagdollScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.world.constraint_iterations = 12
        self.world.substeps = 4

        self.part_density = 0.0002

        self.break_force = 15000.0

        self.parts = {}
        self.connections = []

        self.kick_strength = 200.0
        self.kick_enabled = False

        self.create_ragdoll()

        self.ragdoll_color = self.random_color()

        for body in self.parts.values():
            body.color = self.ragdoll_color

        self.parts["torso"].velocity = Vector2(
            25,
            -10
        )

        self.parts["torso"].angular_velocity = 0.8

    def create_part(
        self,
        name,
        x,
        y,
        radius
    ):

        body = Body(
            x,
            y,
            radius,
            density=self.part_density,
            color=self.random_color()
        )

        body.linear_damping = 0.25
        body.restitution = 0.0
        body.static_friction = 0.7
        body.dynamic_friction = 0.5

        self.parts[name] = body
        self.world.add_body(body)

        return body

    def connect_parts(
        self,
        name1,
        name2
    ):

        body1 = self.parts[name1]
        body2 = self.parts[name2]

        length = (
            body2.position
            - body1.position
        ).length()

        constraint = DistanceConstraint(
            body1,
            body2,
            length,
            compliance=0.00001,
            break_force=self.break_force
        )

        self.world.add_constraint(
            constraint
        )

        self.connections.append(
            (
                body1,
                body2,
                constraint
            )
        )

    def create_ragdoll(self):

        self.create_part(
            "head",
            400,
            170,
            12
        )

        self.create_part(
            "torso",
            400,
            215,
            20
        )

        self.create_part(
            "left_upper_arm",
            365,
            230,
            7
        )

        self.create_part(
            "left_lower_arm",
            330,
            265,
            6
        )

        self.create_part(
            "left_hand",
            305,
            300,
            6
        )

        self.create_part(
            "right_upper_arm",
            435,
            230,
            7
        )

        self.create_part(
            "right_lower_arm",
            470,
            265,
            6
        )

        self.create_part(
            "right_hand",
            495,
            300,
            6
        )

        self.create_part(
            "left_upper_leg",
            385,
            275,
            8
        )

        self.create_part(
            "left_lower_leg",
            370,
            325,
            7
        )

        self.create_part(
            "left_foot",
            360,
            375,
            7
        )

        self.create_part(
            "right_upper_leg",
            415,
            275,
            8
        )

        self.create_part(
            "right_lower_leg",
            430,
            325,
            7
        )

        self.create_part(
            "right_foot",
            440,
            375,
            7
        )

        self.connect_parts(
            "head",
            "torso"
        )

        self.connect_parts(
            "torso",
            "left_upper_arm"
        )

        self.connect_parts(
            "left_upper_arm",
            "left_lower_arm"
        )

        self.connect_parts(
            "left_lower_arm",
            "left_hand"
        )

        self.connect_parts(
            "torso",
            "right_upper_arm"
        )

        self.connect_parts(
            "right_upper_arm",
            "right_lower_arm"
        )

        self.connect_parts(
            "right_lower_arm",
            "right_hand"
        )

        self.connect_parts(
            "torso",
            "left_upper_leg"
        )

        self.connect_parts(
            "left_upper_leg",
            "left_lower_leg"
        )

        self.connect_parts(
            "left_lower_leg",
            "left_foot"
        )

        self.connect_parts(
            "torso",
            "right_upper_leg"
        )

        self.connect_parts(
            "right_upper_leg",
            "right_lower_leg"
        )

        self.connect_parts(
            "right_lower_leg",
            "right_foot"
        )

    def kick_ragdoll(self):

        torso = self.parts["torso"]

        impulse = Vector2(
            self.kick_strength,
            -self.kick_strength * 0.4
        )

        torso.apply_impulse(
            impulse
        )

        torso.wake()

    def update(self, dt):

        if self.kick_enabled:

            self.kick_enabled = False
            self.kick_ragdoll()

        super().update(dt)

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                self.kick_enabled = True

            elif event.key == pygame.K_z:

                self.kick_strength = max(
                    0.0,
                    self.kick_strength - 10.0
                )

            elif event.key == pygame.K_x:

                self.kick_strength = min(
                    500.0,
                    self.kick_strength + 10.0
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

    def draw_connection(
        self,
        renderer,
        body1,
        body2,
        constraint
    ):

        if constraint.broken:

            if constraint.break_position is None:
                return

            position = (
                renderer.camera.world_to_screen(
                    constraint.break_position
                )
            )

            pygame.draw.circle(
                renderer.screen,
                (255, 70, 70),
                (
                    int(position.x),
                    int(position.y)
                ),
                max(
                    4,
                    int(6 * renderer.camera.zoom)
                )
            )

            return

        position1 = (
            renderer.camera.world_to_screen(
                body1.position
            )
        )

        position2 = (
            renderer.camera.world_to_screen(
                body2.position
            )
        )

        pygame.draw.line(
            renderer.screen,
            (180, 180, 180),
            (
                int(position1.x),
                int(position1.y)
            ),
            (
                int(position2.x),
                int(position2.y)
            ),
            max(
                2,
                int(4 * renderer.camera.zoom)
            )
        )

    def draw(self, renderer):

        broken_count = 0

        for body1, body2, constraint in self.connections:

            self.draw_connection(
                renderer,
                body1,
                body2,
                constraint
            )

            if constraint.broken:
                broken_count += 1

        for body in self.parts.values():

            renderer.draw_body(
                body
            )

        text = renderer.font.render(
            (
                f"Parts: {len(self.parts)}  "
                f"Broken: {broken_count}/{len(self.connections)}  "
                f"Break Force: {self.break_force:.0f}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "SPACE: Kick  Z/X: Kick Strength",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )