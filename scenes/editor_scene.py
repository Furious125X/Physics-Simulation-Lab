import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene


class EditorScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 500
        self.world.floor_y = 550

        self.body_radius = 20
        self.body_density = 0.002

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

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                return

            mouse_x, mouse_y = pygame.mouse.get_pos()

            mouse_position = Vector2(
                mouse_x,
                mouse_y
            )

            if self.camera is not None:

                world_position = (
                    self.camera.screen_to_world(
                        mouse_position
                    )
                )

            else:

                world_position = mouse_position

            self.create_body(
                world_position
            )

    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            (
                f"Bodies: {len(self.world.bodies)}  "
                f"Radius: {self.body_radius}"
            ),
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )

        controls = renderer.font.render(
            "LEFT CLICK: Create Body",
            True,
            (200, 200, 200)
        )

        renderer.screen.blit(
            controls,
            (10, 135)
        )