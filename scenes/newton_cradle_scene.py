from physics.body import Body
from physics.constraints import AnchorConstraint
from physics.vector import Vector2

from scenes.base_scene import Scene

class NewtonCradleScene(Scene):

    def __init__(self):

        super().__init__()

        ball_count = 5
        radius = 18
        spacing = radius * 2
        rope_length = 150

        start_x = 300
        anchor_y = 100

        self.first_ball = None

        for i in range(ball_count):

            anchor = Vector2(
                start_x + i * spacing,
                anchor_y
            )

            ball = Body(
                anchor.x,
                anchor.y + rope_length,
                radius,
                color=self.random_color()
            )

            constraint = AnchorConstraint(
                ball,
                anchor,
                rope_length
            )

            self.world.add_body(ball)
            self.world.add_constraint(constraint)

            if i == 0:
                self.first_ball = ball

        # Pull the first ball back so it starts swinging
        self.first_ball.position.x -= 120