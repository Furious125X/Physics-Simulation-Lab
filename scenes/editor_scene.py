import pygame
import math

from physics.body import Body
from physics.spring import Spring
from physics.vector import Vector2

from scenes.base_scene import Scene

from physics.constraints import (AnchorConstraint, DistanceConstraint)


class EditorScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.body_radius = 20
        self.body_density = 0.002

        self.drag_offset = Vector2()

        self.spring_stiffness = 100.0
        self.spring_start_body = None

        self.constraint_start_body = None
        self.anchor_start_body = None

        self.inspected_body = None

        self.paused = False
        self.step_requests = 0

        self.undo_stack = []
        self.drag_start_state = None

    def record_undo(self, action):

        self.undo_stack.append(action)

    def capture_property_state(self, body):

        return {
            "radius": body.radius,
            "mass": body.mass,
            "inverse_mass": body.inverse_mass,
            "inertia": body.inertia,
            "inverse_inertia": body.inverse_inertia,
            "restitution": body.restitution,
            "static_friction": body.static_friction,
            "dynamic_friction": body.dynamic_friction
        }

    def capture_transform_state(self, body):

        return {
            "position": body.position.copy(),
            "previous_position": body.previous_position.copy(),
            "velocity": body.velocity.copy(),
            "angular_velocity": body.angular_velocity,
            "angle": body.angle
        }

    def restore_transform_state(self, body, state):

        body.position = state["position"].copy()
        body.previous_position = state["previous_position"].copy()
        body.velocity = state["velocity"].copy()
        body.angular_velocity = state["angular_velocity"]
        body.angle = state["angle"]

        body.wake()

    def record_property_change(self, body, previous_state):

        current_state = self.capture_property_state(body)

        if current_state != previous_state:

            self.record_undo({
                "type": "body_properties",
                "body": body,
                "state": previous_state
            })

    def finish_body_drag(self):

        body = self.selected_body
        previous_state = self.drag_start_state

        if body is not None and previous_state is not None:

            previous_position = previous_state["position"]

            if (
                body.position.x != previous_position.x
                or body.position.y != previous_position.y
            ):

                self.record_undo({
                    "type": "move_body",
                    "body": body,
                    "state": previous_state
                })

        self.drag_start_state = None

    def undo(self):

        if not self.undo_stack:
            return

        action = self.undo_stack.pop()
        action_type = action["type"]

        if action_type == "create_body":

            body = action["body"]

            for spring in list(self.world.springs):

                if spring.body1 is body or spring.body2 is body:
                    self.world.springs.remove(spring)

            for constraint in list(self.world.constraints):

                if (
                    getattr(constraint, "body", None) is body
                    or getattr(constraint, "body1", None) is body
                    or getattr(constraint, "body2", None) is body
                ):
                    self.world.constraints.remove(constraint)

            if body in self.world.bodies:
                self.world.bodies.remove(body)

            if self.selected_body is body:
                self.selected_body = None
                self.drag_offset = Vector2()

            if self.inspected_body is body:
                self.inspected_body = None

            if self.spring_start_body is body:
                self.spring_start_body = None

            if self.constraint_start_body is body:
                self.constraint_start_body = None

            if self.anchor_start_body is body:
                self.anchor_start_body = None

        elif action_type == "delete_body":

            body = action["body"]
            body_index = action["body_index"]

            self.world.bodies.insert(
                min(body_index, len(self.world.bodies)),
                body
            )

            for index, spring in sorted(action["springs"]):

                self.world.springs.insert(
                    min(index, len(self.world.springs)),
                    spring
                )

            for index, constraint in sorted(action["constraints"]):

                self.world.constraints.insert(
                    min(index, len(self.world.constraints)),
                    constraint
                )

            self.inspected_body = body

        elif action_type == "create_spring":

            spring = action["spring"]

            if spring in self.world.springs:
                self.world.springs.remove(spring)

        elif action_type == "create_constraint":

            constraint = action["constraint"]

            if constraint in self.world.constraints:
                self.world.constraints.remove(constraint)

        elif action_type == "move_body":

            self.restore_transform_state(
                action["body"],
                action["state"]
            )

        elif action_type == "body_properties":

            body = action["body"]

            for name, value in action["state"].items():
                setattr(body, name, value)

            body.wake()

        elif action_type == "spring_stiffness":

            self.spring_stiffness = action["value"]

    def create_body(
        self,
        position
    ):

        body = Body(
            position.x,
            position.y,
            self.body_radius,
            density=self.body_density,
            color=self.random_color()
        )

        body.linear_damping = 0.8
        body.restitution = 0.8
        body.static_friction = 0.6
        body.dynamic_friction = 0.4

        self.world.add_body(body)

        self.record_undo({
            "type": "create_body",
            "body": body
        })

        return body

    def adjust_body_radius(self, change):

        body = self.inspected_body

        if body is None:
            return

        previous_state = self.capture_property_state(body)

        new_radius = max(
            5.0,
            min(
                100.0,
                body.radius + change
            )
        )

        if new_radius == body.radius:
            return

        if not body.is_static:

            density = (
                body.mass
                / (
                    math.pi
                    * body.radius
                    * body.radius
                )
            )

        body.radius = new_radius

        if not body.is_static:

            body.mass = (
                density
                * math.pi
                * body.radius
                * body.radius
            )

            body.inverse_mass = 1 / body.mass

            body.inertia = (
                0.5
                * body.mass
                * body.radius
                * body.radius
            )

            body.inverse_inertia = 1 / body.inertia

        body.wake()
        self.record_property_change(body, previous_state)

    def adjust_body_density(self, factor):

        body = self.inspected_body

        if body is None or body.is_static or body.radius <= 0:
            return

        previous_state = self.capture_property_state(body)

        density = (
            body.mass
            / (
                math.pi
                * body.radius
                * body.radius
            )
        )

        new_density = max(
            0.0001,
            min(
                0.1,
                density * factor
            )
        )

        if new_density == density:
            return

        body.mass = (
            new_density
            * math.pi
            * body.radius
            * body.radius
        )

        body.inverse_mass = 1 / body.mass

        body.inertia = (
            0.5
            * body.mass
            * body.radius
            * body.radius
        )

        body.inverse_inertia = 1 / body.inertia

        body.wake()
        self.record_property_change(body, previous_state)

    def adjust_body_restitution(self, change):

        body = self.inspected_body

        if body is None:
            return

        previous_state = self.capture_property_state(body)

        body.restitution = round(
            max(
                0.0,
                min(
                    1.0,
                    body.restitution + change
                )
            ),
            2
        )

        body.wake()
        self.record_property_change(body, previous_state)

    def adjust_body_friction(
        self,
        friction_type,
        change
    ):

        body = self.inspected_body

        if body is None:
            return

        previous_state = self.capture_property_state(body)

        if friction_type == "static":

            body.static_friction = round(
                max(
                    0.0,
                    min(
                        1.0,
                        body.static_friction + change
                    )
                ),
                2
            )

        elif friction_type == "dynamic":

            body.dynamic_friction = round(
                max(
                    0.0,
                    min(
                        1.0,
                        body.dynamic_friction + change
                    )
                ),
                2
            )

        body.wake()
        self.record_property_change(body, previous_state)

    def delete_body(
        self,
        position
    ):

        body = self.find_body_at_position(
            position
        )

        if body is None:
            return

        body_index = self.world.bodies.index(body)

        spring_records = [
            (index, spring)
            for index, spring in enumerate(self.world.springs)
            if spring.body1 is body or spring.body2 is body
        ]

        springs_to_remove = [
            spring
            for index, spring in spring_records
        ]

        for spring in springs_to_remove:

            self.world.springs.remove(
                spring
            )

        constraint_records = [
            (index, constraint)
            for index, constraint in enumerate(self.world.constraints)
            if (
                getattr(constraint, "body", None) is body
                or getattr(constraint, "body1", None) is body
                or getattr(constraint, "body2", None) is body
            )
        ]

        constraints_to_remove = [
            constraint
            for index, constraint in constraint_records
        ]

        for constraint in constraints_to_remove:

            self.world.constraints.remove(
                constraint
            )

        if self.selected_body is body:

            self.selected_body = None
            self.drag_offset = Vector2()
            self.drag_start_state = None

        if self.inspected_body is body:

            self.inspected_body = None

        if self.spring_start_body is body:

            self.spring_start_body = None

        if self.constraint_start_body is body:

            self.constraint_start_body = None

        if self.anchor_start_body is body:

            self.anchor_start_body = None

        self.world.bodies.remove(
            body
        )

        self.record_undo({
            "type": "delete_body",
            "body": body,
            "body_index": body_index,
            "springs": spring_records,
            "constraints": constraint_records
        })

    def create_spring(
        self,
        body1,
        body2
    ):

        if body1 is body2:
            return

        for spring in self.world.springs:

            if (
                (
                    spring.body1 is body1
                    and spring.body2 is body2
                )
                or
                (
                    spring.body1 is body2
                    and spring.body2 is body1
                )
            ):
                return

        rest_length = (
            body2.position
            - body1.position
        ).length()

        spring = Spring(
            body1,
            body2,
            rest_length,
            self.spring_stiffness
        )

        self.world.add_spring(
            spring
        )

        self.record_undo({
            "type": "create_spring",
            "spring": spring
        })

    def create_distance_constraint(
        self,
        body1,
        body2
    ):

        if body1 is body2:
            return

        for constraint in self.world.constraints:

            if (
                isinstance(
                    constraint,
                    DistanceConstraint
                )
                and not constraint.broken
                and (
                    (
                        constraint.body1 is body1
                        and constraint.body2 is body2
                    )
                    or
                    (
                        constraint.body1 is body2
                        and constraint.body2 is body1
                    )
                )
            ):
                return

        length = (
            body2.position
            - body1.position
        ).length()

        constraint = DistanceConstraint(
            body1,
            body2,
            length,
            compliance=0.00001
        )

        self.world.add_constraint(
            constraint
        )

        self.record_undo({
            "type": "create_constraint",
            "constraint": constraint
        })

    def create_anchor_constraint(
        self,
        body,
        anchor
    ):

        length = (
            body.position
            - anchor
        ).length()

        constraint = AnchorConstraint(
            body,
            anchor.copy(),
            length,
            compliance=0.00001
        )

        self.world.add_constraint(
            constraint
        )

        self.record_undo({
            "type": "create_constraint",
            "constraint": constraint
        })

    def get_mouse_world_position(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()

        mouse_position = Vector2(
            mouse_x,
            mouse_y
        )

        if self.camera is not None:

            return self.camera.screen_to_world(
                mouse_position
            )

        return mouse_position

    def update(self, dt):

        if self.paused:

            if self.step_requests > 0:
                self.world.update(dt)
                self.step_requests -= 1

        else:
            self.step_requests = 0
            self.world.update(dt)

        if self.selected_body is not None:

            mouse_position = (
                self.get_mouse_world_position()
            )

            self.selected_body.position = (
                mouse_position
                + self.drag_offset
            )

            self.selected_body.previous_position = (
                self.selected_body.position.copy()
            )

            self.selected_body.velocity = Vector2()
            self.selected_body.angular_velocity = 0.0

            self.selected_body.wake()

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            modifiers = getattr(
                event,
                "mod",
                pygame.key.get_mods()
            )

            if (
                event.key == pygame.K_z
                and modifiers & pygame.KMOD_CTRL
            ):

                self.finish_body_drag()
                self.selected_body = None
                self.drag_offset = Vector2()
                self.undo()

            elif event.key == pygame.K_SPACE:

                self.paused = not self.paused

            elif event.key == pygame.K_RETURN:

                if self.paused:
                    self.step_requests += 1

            elif event.key == pygame.K_ESCAPE:

                self.finish_body_drag()
                self.spring_start_body = None
                self.constraint_start_body = None
                self.anchor_start_body = None

                self.selected_body = None
                self.drag_offset = Vector2()

            elif event.key == pygame.K_z:

                previous_stiffness = self.spring_stiffness

                self.spring_stiffness = max(
                    25.0,
                    self.spring_stiffness - 25.0
                )

                if self.spring_stiffness != previous_stiffness:

                    self.record_undo({
                        "type": "spring_stiffness",
                        "value": previous_stiffness
                    })

            elif event.key == pygame.K_x:

                previous_stiffness = self.spring_stiffness

                self.spring_stiffness = min(
                    1000.0,
                    self.spring_stiffness + 25.0
                )

                if self.spring_stiffness != previous_stiffness:

                    self.record_undo({
                        "type": "spring_stiffness",
                        "value": previous_stiffness
                    })

            elif event.key == pygame.K_LEFTBRACKET:

                self.adjust_body_radius(-2.0)

            elif event.key == pygame.K_RIGHTBRACKET:

                self.adjust_body_radius(2.0)

            elif event.key == pygame.K_COMMA:

                self.adjust_body_density(0.8)

            elif event.key == pygame.K_PERIOD:

                self.adjust_body_density(1.25)

            elif event.key == pygame.K_QUOTE:

                self.adjust_body_restitution(0.1)

            elif event.key == pygame.K_SEMICOLON:

                self.adjust_body_restitution(-0.1)

            elif event.key == pygame.K_F11:

                self.adjust_body_friction(
                    "static",
                    -0.1
                )

            elif event.key == pygame.K_F12:

                self.adjust_body_friction(
                    "static",
                    0.1
                )

            elif event.key == pygame.K_BACKSLASH:

                self.adjust_body_friction(
                    "dynamic",
                    -0.1
                )

            elif event.key == pygame.K_SLASH:

                self.adjust_body_friction(
                    "dynamic",
                    0.1
                )

        if event.type == pygame.MOUSEBUTTONDOWN:

            world_position = (
                self.get_mouse_world_position()
            )

            if event.button == 1:

                body = (
                    self.find_body_at_position(
                        world_position
                    )
                )

                modifiers = pygame.key.get_mods()

                if modifiers & pygame.KMOD_SHIFT:

                    if body is None:
                        return

                    if self.spring_start_body is None:

                        self.spring_start_body = body
                        self.constraint_start_body = None
                        self.anchor_start_body = None
                        self.inspected_body = body

                    else:

                        self.create_spring(
                            self.spring_start_body,
                            body
                        )

                        self.spring_start_body = None

                elif modifiers & pygame.KMOD_CTRL:

                    if body is None:
                        return

                    if self.constraint_start_body is None:

                        self.constraint_start_body = body
                        self.spring_start_body = None
                        self.anchor_start_body = None
                        self.inspected_body = body

                    else:

                        self.create_distance_constraint(
                            self.constraint_start_body,
                            body
                        )

                        self.constraint_start_body = None

                elif modifiers & pygame.KMOD_ALT:

                    if self.anchor_start_body is None:

                        if body is None:
                            return

                        self.anchor_start_body = body
                        self.spring_start_body = None
                        self.constraint_start_body = None
                        self.inspected_body = body

                    else:

                        self.create_anchor_constraint(
                            self.anchor_start_body,
                            world_position
                        )

                        self.anchor_start_body = None

                elif body is not None:

                    self.selected_body = body
                    self.inspected_body = body
                    self.drag_start_state = self.capture_transform_state(body)

                    self.drag_offset = (
                        body.position
                        - world_position
                    )

                    body.wake()

                else:

                    self.inspected_body = (
                        self.create_body(
                            world_position
                        )
                    )

            elif event.button == 3:

                self.delete_body(
                    world_position
                )

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                self.finish_body_drag()
                self.selected_body = None
                self.drag_offset = Vector2()

    def draw(self, renderer):

        self.world.draw(renderer)

        if self.selected_body is not None:

            self.draw_body_outline(
                renderer,
                self.selected_body,
                (255, 220, 80),
                4
            )

        if self.spring_start_body is not None:

            self.draw_body_outline(
                renderer,
                self.spring_start_body,
                (255, 120, 80),
                7
            )

        if self.constraint_start_body is not None:

            self.draw_body_outline(
                renderer,
                self.constraint_start_body,
                (100, 220, 255),
                7
            )

        if self.anchor_start_body is not None:

            self.draw_body_outline(
                renderer,
                self.anchor_start_body,
                (190, 120, 255),
                7
            )

        text = renderer.font.render(
            (
                f"Bodies: {len(self.world.bodies)}  "
                f"Springs: {len(self.world.springs)}  "
                f"Constraints: {len(self.world.constraints)}  "
                f"New Radius: {self.body_radius}  "
                f"Stiffness: {self.spring_stiffness:.0f}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            (
                "LEFT CLICK: Create / Move  "
                "RIGHT CLICK: Delete"
            ),
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )

        spring_controls = renderer.font.render(
            (
                "SHIFT + CLICK x2: Spring  "
                "Z/X: Stiffness"
            ),
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            spring_controls,
            (10, 160)
        )

        constraint_controls = renderer.font.render(
            (
                "CTRL + CLICK x2: Distance  "
                "ALT + CLICK: Anchor  ESC: Cancel"
            ),
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            constraint_controls,
            (10, 185)
        )

        radius_controls = renderer.font.render(
            "[ / ]: Decrease / Increase Inspected Radius",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            radius_controls,
            (10, 210)
        )

        density_controls = renderer.font.render(
            ", / .: Decrease / Increase Inspected Density",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            density_controls,
            (10, 235)
        )

        restitution_controls = renderer.font.render(
            "Semicolon / Quote: Decrease / Increase Restitution",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            restitution_controls,
            (10, 260)
        )

        friction_controls = renderer.font.render(
            "F11/F12: Static Friction  HOME/END: Dynamic Friction",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            friction_controls,
            (10, 285)
        )

        pause_controls = renderer.font.render(
            "SPACE: Pause / Resume Simulation",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            pause_controls,
            (10, 310)
        )

        step_controls = renderer.font.render(
            "ENTER: Step one physics tick (paused)",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            step_controls,
            (10, 335)
        )

        undo_controls = renderer.font.render(
            "CTRL+Z: Undo Last Edit",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            undo_controls,
            (10, 360)
        )

        if self.paused:

            paused_text = renderer.font.render(
                "PAUSED - Physics frozen",
                True,
                (255, 100, 100)
            )

            renderer.screen.blit(
                paused_text,
                (10, 385)
            )

        self.draw_property_inspector(
            renderer
        )

    def draw_body_outline(
        self,
        renderer,
        body,
        color,
        padding
    ):

        screen_position = (
            renderer.camera.world_to_screen(
                body.position
            )
        )

        pygame.draw.circle(
            renderer.screen,
            color,
            (
                int(screen_position.x),
                int(screen_position.y)
            ),
            max(
                3,
                int(
                    (
                        body.radius
                        + padding
                    )
                    * renderer.camera.zoom
                )
            ),
            3
        )

    def draw_property_inspector(self, renderer):

        panel_rect = pygame.Rect(
            550,
            92,
            240,
            330
        )

        pygame.draw.rect(
            renderer.screen,
            (18, 18, 24),
            panel_rect
        )

        pygame.draw.rect(
            renderer.screen,
            (100, 100, 110),
            panel_rect,
            1
        )

        title = renderer.font.render(
            "PROPERTY INSPECTOR",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            title,
            (560, 101)
        )

        pygame.draw.line(
            renderer.screen,
            (100, 100, 110),
            (560, 128),
            (780, 128),
            1
        )

        body = self.inspected_body

        if body is None:

            text = renderer.font.render(
                "Click a body to inspect.",
                True,
                (180, 180, 180)
            )

            renderer.screen.blit(
                text,
                (560, 140)
            )

            return

        if body.is_static:

            mass_text = "Infinite"
            density_text = "N/A"

        else:

            mass_text = f"{body.mass:.3f}"

            if body.radius > 0:

                density = (
                    body.mass
                    / (
                        math.pi
                        * body.radius
                        * body.radius
                    )
                )

                density_text = f"{density:.5f}"

            else:

                density_text = "N/A"

        body_type = (
            "Static"
            if body.is_static
            else "Dynamic"
        )

        body_state = (
            "Sleeping"
            if body.sleeping
            else "Awake"
        )

        properties = [
            f"ID: {body.id}",
            f"Type: {body_type}",
            (
                f"Pos: "
                f"{body.position.x:.1f}, "
                f"{body.position.y:.1f}"
            ),
            f"Radius: {body.radius:.1f}",
            f"Mass: {mass_text}",
            f"Density: {density_text}",
            f"Restitution: {body.restitution:.2f}",
            f"Static friction: {body.static_friction:.2f}",
            f"Dynamic friction: {body.dynamic_friction:.2f}",
            (
                f"Vel: "
                f"{body.velocity.x:.1f}, "
                f"{body.velocity.y:.1f}"
            ),
            f"Angular vel: {body.angular_velocity:.2f}",
            f"Angle: {body.angle:.2f} rad",
            f"State: {body_state}"
        ]

        y = 135

        for property_text in properties:

            text = renderer.font.render(
                property_text,
                True,
                (220, 220, 220)
            )

            renderer.screen.blit(
                text,
                (560, y)
            )

            y += 20