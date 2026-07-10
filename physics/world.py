from physics.grid import SpatialGrid

class World:
    def __init__(self, gravity=500, floor_y=600):
        self.gravity = gravity
        self.floor_y = floor_y
        self.bodies = []
        self.springs = []
        self.constraints = []
        self.grid = SpatialGrid(100)

    def add_body(self, body):
        self.bodies.append(body)

    def add_spring(self, spring):
        self.springs.append(spring)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        


    def update(self, dt):
        for spring in self.springs:
            spring.update()
        for body in self.bodies:
            body.gravity = self.gravity
            body.update(dt, self.floor_y)
        for constraint in self.constraints:
            constraint.solve()

        self.grid.build(self.bodies)
        self.check_collisions()

    def draw(self, renderer):
        for spring in self.springs:
            renderer.draw_spring(spring)
        for body in self.bodies:
            renderer.draw_body(body)
        for constraint in self.constraints:
            renderer.draw_constraint(constraint)

    def check_collisions(self):
        for cell in self.grid.cells.values():
            for i in range(len(cell)):
                for j in range(i + 1, len(cell)):
                    body1 = cell[i]
                    body2 = cell[j]

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