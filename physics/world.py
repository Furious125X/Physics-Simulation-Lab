class World:
    def __init__(self, gravity=500, floor_y=600):
        self.gravity = gravity
        self.floor_y = floor_y
        self.bodies = []

    def add_body(self, body):
        self.bodies.append(body)

    def update(self, dt):
        for body in self.bodies:
            body.gravity = self.gravity
            body.update(dt, self.floor_y)

        self.check_collisions()

    def draw(self, renderer):
        for body in self.bodies:
            renderer.draw_body(body)

    def check_collisions(self):
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body1 = self.bodies[i]
                body2 = self.bodies[j]

                difference = body2.position - body1.position
                distance = difference.length()

                radius_sum = body1.radius + body2.radius

                if distance < radius_sum:
                    self.resolve_collision(body1, body2)

    
    def resolve_collision(self, body1, body2):
        difference = body2.position - body1.position
        distance = difference.length()

        if distance == 0:
            return

        radius_sum = body1.radius + body2.radius
        overlap = radius_sum - distance

        collision_normal = difference.normalize()

        body1.position -= collision_normal * (overlap / 2)
        body2.position += collision_normal * (overlap / 2)

        relative_velocity = body2.velocity - body1.velocity
        velocity_along_normal = relative_velocity.dot(collision_normal)
        if velocity_along_normal > 0 :
            return
        e = min(body1.restitution, body2.restitution)
        j = -(1 + e) * velocity_along_normal
        j /= (1 / body1.mass) + (1 / body2.mass)
        impulse = collision_normal * j
        body1.velocity -= impulse * (1 / body1.mass)
        body2.velocity += impulse * (1 / body2.mass)