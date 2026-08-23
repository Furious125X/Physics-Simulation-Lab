from physics.body import Body

from scenes.base_scene import Scene

class StaticCollisionScene(Scene):
    def __init__(self):

        super().__init__()

        ball1 = Body(
            100,
            250,
            20,
            color=self.random_color()
        )

        ball1.velocity.x = 2500

        ball2 = Body(
            650,
            250,
            50,
            color=self.random_color(),
            is_static=True
        )
        self.world.add_body(ball1)
        self.world.add_body(ball2)