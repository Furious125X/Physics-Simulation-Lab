import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene

class ElasticCollisionScene(Scene):

    def __init__(self):

        super().__init__()

        self.world.gravity = 0
        self.world.floor_y = 10000
        self.world.substeps = 1

        self.left_body = Body(
            250,
            300,
            25,
            density=0.002,
            color=self.random_color()
        )

        self.right_body = Body(
            550,
            300,
            25,
            density=0.002,
            color=self.random_color()
        )

        self.left_body.linear_damping = 0.0
        self.right_body.linear_damping = 0.0

        self.left_body.static_friction = 0.0
        self.left_body.dynamic_friction = 0.0

        self.right_body.static_friction = 0.0
        self.right_body.dynamic_friction = 0.0

        self.restitution = 1.0
        self.left_body.restitution = self.restitution
        self.right_body.restitution = self.restitution 


        self.left_body.velocity = Vector2(
            150,
            0
        )

        self.right_body.velocity = Vector2(
            -150,
            0
        )


        self.world.add_body(
            self.left_body
        )

        self.world.add_body(
            self.right_body
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


        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_z:

                self.restitution = max(
                    0.0,
                    self.restitution - 0.1
                )

                self.left_body.restitution = (
                    self.restitution
                )

                self.right_body.restitution = (
                    self.restitution
                )

            elif event.key == pygame.K_x:

                self.restitution = min(
                    1.0,
                    self.restitution + 0.1
                )

                self.left_body.restitution = (
                    self.restitution
                )

                self.right_body.restitution = (
                    self.restitution
                )


    def draw(self, renderer):

        self.world.draw(renderer)

        text = renderer.font.render(
            f"Restitution: {self.restitution:.2f}",
            True,
            (255, 255, 255)
        )

        renderer.screen.blit(
            text,
            (10, 110)
        )


    