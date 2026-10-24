import pygame
import math
import json
import os

from physics.body import Body
from physics.spring import Spring
from physics.vector import Vector2
from physics.world import World

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
        self.redo_stack = []

        self.drag_start_state = None

        self.save_message = ""

    def record_undo(self, action):

        self.undo_stack.append(action)

        self.redo_stack.clear()

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


    def serialize_body(self, body):

        if body.is_static:
            density = None
        else:
            density = (
                body.mass
                / (math.pi * body.radius * body.radius)
            )

        return {
            "id": body.id,

            "position": [
                body.position.x,
                body.position.y
            ],

            "previous_position": [
                body.previous_position.x,
                body.previous_position.y
            ],

            "velocity": [
                body.velocity.x,
                body.velocity.y
            ],

            "radius": body.radius,
            "density": density,
            "color": list(body.color),
            "is_static": body.is_static,

            "angle": body.angle,
            "angular_velocity": body.angular_velocity,

            "restitution": body.restitution,
            "static_friction": body.static_friction,
            "dynamic_friction": body.dynamic_friction,
            "linear_damping": body.linear_damping,

            "sleeping": body.sleeping,
            "sleep_timer": body.sleep_timer
        }

    def serialize_constraint(self, constraint):

        if isinstance(constraint, AnchorConstraint):

            return {
                "type": "anchor",

                "body_id": constraint.body.id,

                "anchor": [
                    constraint.anchor.x,
                    constraint.anchor.y
                ],

                "length": constraint.length,
                "compliance": constraint.compliance
            }

        elif isinstance(constraint, DistanceConstraint):

            if constraint.break_position is None:
                break_position = None
            else:
                break_position = [
                    constraint.break_position.x,
                    constraint.break_position.y
                ]

            return {
                "type": "distance",

                "body1_id": constraint.body1.id,
                "body2_id": constraint.body2.id,

                "length": constraint.length,
                "stiffness": constraint.stiffness,
                "compliance": constraint.compliance,
                "break_force": constraint.break_force,

                "broken": constraint.broken,
                "current_force": constraint.current_force,
                "break_position": break_position
            }

        else:
            raise TypeError(
                f"Unsupported constraint type: "
                f"{type(constraint).__name__}"
            )


    def save_scene(self):

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        save_directory = os.path.join(
            project_root,
            "saved_scenes"
        )

        save_path = os.path.join(
            save_directory,
            "editor_scene.json"
        )

        try:

            os.makedirs(
                save_directory,
                exist_ok=True
            )

            scene_data = {

                "format_version": 1,
                "scene_type": "editor",

                "next_body_id": Body.next_id,

                "world": {
                    "gravity": self.world.gravity,
                    "floor_y": self.world.floor_y,

                    "enable_collisions": (
                        self.world.enable_collisions
                    ),

                    "constraint_iterations": (
                        self.world.constraint_iterations
                    ),

                    "substeps": self.world.substeps,

                    "collision_iterations": (
                        self.world.collision_iterations
                    ),

                    "resting_velocity_threshold": (
                        self.world.resting_velocity_threshold
                    )
                },

                "editor": {
                    "body_radius": self.body_radius,
                    "body_density": self.body_density,
                    "spring_stiffness": self.spring_stiffness
                },

                "bodies": [
                    self.serialize_body(body)
                    for body in self.world.bodies
                ],

                "springs": [
                    {
                        "body1_id": spring.body1.id,
                        "body2_id": spring.body2.id,
                        "rest_length": spring.rest_length,
                        "stiffness": spring.stiffness,
                        "width": spring.width
                    }
                    for spring in self.world.springs
                ],

                "constraints": [
                    self.serialize_constraint(constraint)
                    for constraint in self.world.constraints
                ]
            }

            with open(
                save_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    scene_data,
                    file,
                    indent=4,
                    allow_nan=False
                )

            relative_path = os.path.relpath(
                save_path,
                project_root
            )

            self.save_message = (
                f"Saved: {relative_path}"
            )

            print(self.save_message)

        except (OSError, TypeError, ValueError) as error:

            self.save_message = (
                "Save failed. Check terminal."
            )

            print(
                f"Failed to save editor scene: {error}"
            )


    def load_scene(self):

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        save_directory = os.path.join(
            project_root,
            "saved_scenes"
        )

        save_path = os.path.join(
            save_directory,
            "editor_scene.json"
        )

        previous_next_body_id = Body.next_id

        try:

            with open(
                save_path,
                "r",
                encoding="utf-8"
            ) as file:

                scene_data = json.load(file)

            if scene_data.get("format_version") != 1:
                raise ValueError(
                    "Unsupported scene format version."
                )

            if scene_data.get("scene_type") != "editor":
                raise ValueError(
                    "This file is not an editor scene."
                )

            world_data = scene_data["world"]
            editor_data = scene_data["editor"]

            # ----------------------------------
            # 1. Reconstruct bodies
            # ----------------------------------

            loaded_bodies = []
            bodies_by_id = {}

            for body_data in scene_data["bodies"]:

                density = body_data["density"]

                if density is None:
                    density = 0.002

                body = Body(
                    body_data["position"][0],
                    body_data["position"][1],
                    radius=body_data["radius"],
                    density=density,
                    color=tuple(body_data["color"]),
                    is_static=body_data["is_static"]
                )

                # Restore the saved ID.
                body.id = body_data["id"]

                if body.id in bodies_by_id:
                    raise ValueError(
                        f"Duplicate body ID: {body.id}"
                    )

                # Restore the motion state.
                body.previous_position = Vector2(
                    *body_data["previous_position"]
                )

                body.velocity = Vector2(
                    *body_data["velocity"]
                )

                body.angle = body_data["angle"]
                body.angular_velocity = (
                    body_data["angular_velocity"]
                )

                # Restore material properties.
                body.restitution = body_data["restitution"]
                body.static_friction = (
                    body_data["static_friction"]
                )
                body.dynamic_friction = (
                    body_data["dynamic_friction"]
                )
                body.linear_damping = (
                    body_data["linear_damping"]
                )

                # Restore sleeping state.
                body.sleeping = (
                    True
                    if body.is_static
                    else body_data["sleeping"]
                )

                body.sleep_timer = body_data["sleep_timer"]
                body.gravity = world_data["gravity"]

                # Temporary physics state starts clean.
                body.force = Vector2()
                body.torque = 0.0
                body.impulse_velocity_delta = Vector2()
                body.hit_floor = False
                body.debug_force = Vector2()

                bodies_by_id[body.id] = body
                loaded_bodies.append(body)

            # ----------------------------------
            # 2. Reconstruct springs
            # ----------------------------------

            loaded_springs = []

            for spring_data in scene_data["springs"]:

                body1 = bodies_by_id[
                    spring_data["body1_id"]
                ]

                body2 = bodies_by_id[
                    spring_data["body2_id"]
                ]

                spring = Spring(
                    body1,
                    body2,
                    spring_data["rest_length"],
                    spring_data["stiffness"]
                )

                spring.width = spring_data.get(
                    "width",
                    2
                )

                loaded_springs.append(spring)

            # ----------------------------------
            # 3. Reconstruct constraints
            # ----------------------------------

            loaded_constraints = []

            for constraint_data in scene_data["constraints"]:

                constraint_type = constraint_data["type"]

                if constraint_type == "anchor":

                    body = bodies_by_id[
                        constraint_data["body_id"]
                    ]

                    anchor = Vector2(
                        *constraint_data["anchor"]
                    )

                    constraint = AnchorConstraint(
                        body,
                        anchor,
                        constraint_data["length"],
                        compliance=constraint_data["compliance"]
                    )

                elif constraint_type == "distance":

                    body1 = bodies_by_id[
                        constraint_data["body1_id"]
                    ]

                    body2 = bodies_by_id[
                        constraint_data["body2_id"]
                    ]

                    constraint = DistanceConstraint(
                        body1,
                        body2,
                        constraint_data["length"],
                        stiffness=constraint_data["stiffness"],
                        compliance=constraint_data["compliance"],
                        break_force=constraint_data["break_force"]
                    )

                    constraint.broken = (
                        constraint_data["broken"]
                    )

                    constraint.current_force = (
                        constraint_data["current_force"]
                    )

                    break_position = constraint_data[
                        "break_position"
                    ]

                    if break_position is not None:

                        constraint.break_position = Vector2(
                            *break_position
                        )

                else:

                    raise ValueError(
                        f"Unknown constraint type: "
                        f"{constraint_type}"
                    )

                loaded_constraints.append(constraint)

            # ----------------------------------
            # 4. Reconstruct the world
            # ----------------------------------

            loaded_world = World(
                gravity=world_data["gravity"],
                floor_y=world_data["floor_y"]
            )

            loaded_world.enable_collisions = (
                world_data["enable_collisions"]
            )

            loaded_world.constraint_iterations = (
                world_data["constraint_iterations"]
            )

            loaded_world.substeps = world_data["substeps"]

            loaded_world.collision_iterations = (
                world_data["collision_iterations"]
            )

            loaded_world.resting_velocity_threshold = (
                world_data["resting_velocity_threshold"]
            )

            loaded_world.bodies = loaded_bodies
            loaded_world.springs = loaded_springs
            loaded_world.constraints = loaded_constraints

            # Preserve the current debug-display settings.
            debug_attributes = [
                "debug_draw",
                "show_grid_debug",
                "show_collision_normals",
                "show_velocity_vectors",
                "show_force_vectors",
                "show_bounding_boxes",
                "show_sleeping"
            ]

            for attribute in debug_attributes:

                setattr(
                    loaded_world,
                    attribute,
                    getattr(self.world, attribute)
                )

            # Build the grid immediately, rather than waiting
            # for the next physics update.
            loaded_world.grid.build(loaded_world.bodies)

            # ----------------------------------
            # 5. Replace the active scene
            # ----------------------------------

            self.world = loaded_world

            self.body_radius = editor_data["body_radius"]
            self.body_density = editor_data["body_density"]
            self.spring_stiffness = (
                editor_data["spring_stiffness"]
            )

            # Keep future body IDs unique.
            highest_body_id = max(
                (body.id for body in loaded_bodies),
                default=-1
            )

            Body.next_id = max(
                scene_data["next_body_id"],
                highest_body_id + 1
            )

            # Clear interaction state.
            self.selected_body = None
            self.inspected_body = None
            self.drag_offset = Vector2()
            self.drag_start_state = None

            self.spring_start_body = None
            self.constraint_start_body = None
            self.anchor_start_body = None

            # History refers to the previous world.
            self.undo_stack.clear()
            self.redo_stack.clear()

            self.step_requests = 0

            self.save_message = (
                "Loaded: saved_scenes/editor_scene.json"
            )

            print(self.save_message)

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError
        ) as error:

            # Restore the ID counter if loading failed.
            Body.next_id = previous_next_body_id

            self.save_message = (
                "Load failed. Check terminal."
            )

            print(
                f"Failed to load editor scene: {error}"
            )

    def record_property_change(self, body, previous_state):

        current_state = self.capture_property_state(body)

        if current_state != previous_state:

            self.record_undo({
                "type": "body_properties",
                "body": body,
                "state": previous_state,
                "redo_state": current_state
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
                    "state": previous_state,
                    "redo_state": self.capture_transform_state(body)
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

        self.redo_stack.append(action)

    def redo(self):

        if not self.redo_stack:
            return

        action = self.redo_stack.pop()
        action_type = action["type"]

        if action_type == "create_body":

            body = action["body"]
            body_index = action["body_index"]

            if body not in self.world.bodies:

                self.world.bodies.insert(
                    min(body_index, len(self.world.bodies)),
                    body
                )

            self.inspected_body = body

        elif action_type == "delete_body":

            body = action["body"]

            for _, spring in action["springs"]:

                if spring in self.world.springs:
                    self.world.springs.remove(spring)

            for _, constraint in action["constraints"]:

                if constraint in self.world.constraints:
                    self.world.constraints.remove(constraint)

            if body in self.world.bodies:
                self.world.bodies.remove(body)

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

        elif action_type == "create_spring":

            spring = action["spring"]
            spring_index = action["spring_index"]

            if spring not in self.world.springs:

                self.world.springs.insert(
                    min(spring_index, len(self.world.springs)),
                    spring
                )

        elif action_type == "create_constraint":

            constraint = action["constraint"]
            constraint_index = action["constraint_index"]

            if constraint not in self.world.constraints:

                self.world.constraints.insert(
                    min(constraint_index, len(self.world.constraints)),
                    constraint
                )

        elif action_type == "move_body":

            self.restore_transform_state(
                action["body"],
                action["redo_state"]
            )

        elif action_type == "body_properties":

            body = action["body"]

            for name, value in action["redo_state"].items():
                setattr(body, name, value)

            body.wake()

        elif action_type == "spring_stiffness":

            self.spring_stiffness = action["redo_value"]

        self.undo_stack.append(action)

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
            "body": body,
            "body_index": self.world.bodies.index(body)
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
            "spring": spring,
            "spring_index": self.world.springs.index(spring)
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
            "constraint": constraint,
            "constraint_index": self.world.constraints.index(constraint)
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
            "constraint": constraint,
            "constraint_index": self.world.constraints.index(constraint)
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
                event.key == pygame.K_o
                and modifiers & pygame.KMOD_CTRL
            ):

                self.load_scene()

            elif (
                event.key == pygame.K_s
                and modifiers & pygame.KMOD_CTRL
            ):

                self.save_scene()
            
            elif (
                event.key == pygame.K_y
                and modifiers & pygame.KMOD_CTRL
            ) :

                self.redo()
                
            elif (
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
                        "value": previous_stiffness,
                        "redo_value": self.spring_stiffness
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
                        "value": previous_stiffness,
                        "redo_value": self.spring_stiffness
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

        save_controls = renderer.font.render(
            "CTRL+S: Save Scene",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            save_controls,
            (10, 385)
        )

        load_controls = renderer.font.render(
            "CTRL+O: Load Scene",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            load_controls,
            (10, 410)
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

        if self.save_message:

            if self.save_message.startswith(
                ("Saved:", "Loaded:")
            ):
                status_color = (120, 255, 150)
            else:
                status_color = (255, 100, 100)

            save_status = renderer.font.render(
                self.save_message,
                True,
                status_color
            )

            renderer.screen.blit(
                save_status,
                (10, 435)
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