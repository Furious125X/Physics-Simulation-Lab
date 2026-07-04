class Spring:
    def __init__(self, body1, body2, rest_length, stiffness):
        self.body1 = body1
        self.body2 = body2
        self.rest_length = rest_length
        self.stiffness = stiffness
    
    def update(self):
        difference = self.body2.position - self.body1.position
        current_length = difference.length()
        stretch = current_length - self.rest_length
        direction = difference.normalize()
        force = self.stiffness * stretch
        force_vector = direction * force
        self.body1.apply_force(force_vector)
        self.body2.apply_force(-force_vector)
