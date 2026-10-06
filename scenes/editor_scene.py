import pygame

from physics.body import Body
from physics.spring import Spring
from physics.vector import Vector2

from scenes.base_scene import Scene


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

    def delete_body(
        self,
        position
    ):

        body = self.find_body_at_position(
            position
        )

        if body is None:
            return

        springs_to_remove = []

        for spring in self.world.springs:

            if (
                spring.body1 is body
                or spring.body2 is body
            ):

                springs_to_remove.append(
                    spring
                )

        for spring in springs_to_remove:

            self.world.springs.remove(
                spring
            )

        if self.selected_body is body:

            self.selected_body = None
            self.drag_offset = Vector2()

        if self.spring_start_body is body:

            self.spring_start_body = None

        self.world.bodies.remove(
            body
        )

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

            if event.key == pygame.K_ESCAPE:

                self.spring_start_body = None

            elif event.key == pygame.K_z:

                self.spring_stiffness = max(
                    25.0,
                    self.spring_stiffness - 25.0
                )

            elif event.key == pygame.K_x:

                self.spring_stiffness = min(
                    1000.0,
                    self.spring_stiffness + 25.0
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

                if pygame.key.get_mods() & pygame.KMOD_SHIFT:

                    if body is None:
                        return

                    if self.spring_start_body is None:

                        self.spring_start_body = body

                    else:

                        self.create_spring(
                            self.spring_start_body,
                            body
                        )

                        self.spring_start_body = None

                elif body is not None:

                    self.selected_body = body

                    self.drag_offset = (
                        body.position
                        - world_position
                    )

                    body.wake()

                else:

                    self.create_body(
                        world_position
                    )

            elif event.button == 3:

                self.delete_body(
                    world_position
                )

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:

                self.selected_body = None
                self.drag_offset = Vector2()

    def draw(self, renderer):

        self.world.draw(renderer)

        if self.selected_body is not None:

            screen_position = (
                renderer.camera.world_to_screen(
                    self.selected_body.position
                )
            )

            pygame.draw.circle(
                renderer.screen,
                (255, 220, 80),
                (
                    int(screen_position.x),
                    int(screen_position.y)
                ),
                max(
                    2,
                    int(
                        (
                            self.selected_body.radius
                            + 4
                        )
                        * renderer.camera.zoom
                    )
                ),
                3
            )

        if self.spring_start_body is not None:

            screen_position = (
                renderer.camera.world_to_screen(
                    self.spring_start_body.position
                )
            )

            pygame.draw.circle(
                renderer.screen,
                (255, 120, 80),
                (
                    int(screen_position.x),
                    int(screen_position.y)
                ),
                max(
                    3,
                    int(
                        (
                            self.spring_start_body.radius
                            + 7
                        )
                        * renderer.camera.zoom
                    )
                ),
                3
            )

        text = renderer.font.render(
            (
                f"Bodies: {len(self.world.bodies)}  "
                f"Springs: {len(self.world.springs)}  "
                f"Radius: {self.body_radius}  "
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
                "SHIFT + LEFT CLICK: Create Spring  "
                "ESC: Cancel  Z/X: Stiffness"
            ),
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            spring_controls,
            (10, 160)
        )