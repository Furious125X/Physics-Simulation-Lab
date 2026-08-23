import random
import pygame

from physics.body import Body
from physics.constraints import (
    AnchorConstraint,
    DistanceConstraint
)
from physics.vector import Vector2

from scenes.base_scene import Scene

class RopeScene(Scene):

    def __init__(self):

        super().__init__()

        segments = 20
        segment_radius = 8
        segment_length = 20

        start_x = 400
        start_y = 50
        anchor = Vector2(start_x, start_y)

        self.rope_bodies = []
        for i in range(segments):

            segment = Body(start_x, start_y  + segment_length * i, segment_radius, color=self.random_color())
            self.rope_bodies.append(segment)
            self.world.add_body(segment)
        
        first_segment = AnchorConstraint(self.rope_bodies[0], anchor, 0)
        self.world.add_constraint(first_segment)

        for i  in range(len(self.rope_bodies) - 1) :
            connector = DistanceConstraint(self.rope_bodies[i], self.rope_bodies[i+1], segment_length)
            self.world.add_constraint(connector)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_position = Vector2(mouse_x, mouse_y)

            self.selected_body = self.find_body_at_position(mouse_position)

        elif event.type == pygame.MOUSEBUTTONUP:

            self.selected_body = None

        elif event.type == pygame.MOUSEWHEEL:

            mouse_x, mouse_y = pygame.mouse.get_pos()

            body = Body(
                mouse_x,
                mouse_y,
                random.randint(10, 40),
                color=self.random_color()
            )

            self.world.add_body(body)
