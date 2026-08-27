import pygame

from physics.body import Body
from physics.vector import Vector2

from scenes.base_scene import Scene

class ProjectileScene(Scene):

    def __init__(self):

        super().__init__()

        start_position = Vector2(
            100,
            450
        )

        launch_velocity = Vector2(
            300,
            -350
        )

        radius = 15

        projectile = Body(
            start_position.x,
            start_position.y,
            radius,
            color=self.random_color()
        )

        projectile.linear_damping = 0.0
        projectile.velocity = launch_velocity
        projectile.restitution = 0.3
        
        self.world.add_body(projectile)


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