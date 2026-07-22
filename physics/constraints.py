class AnchorConstraint:
    def __init__(self, body, anchor, length):
        self.body = body
        self.anchor = anchor
        self.length = length

    def solve(self):
        difference = self.body.position - self.anchor

        if difference.length() == 0:
            return

        direction = difference.normalize()
        self.body.position = self.anchor + direction * self.length


class DistanceConstraint:
    def __init__(self, body1, body2, length):
        self.body1 = body1
        self.body2 = body2
        self.length = length

    def solve(self):
        difference = self.body2.position - self.body1.position

        distance = difference.length()

        inv_mass1 = self.body1.inverse_mass
        inv_mass2 = self.body2.inverse_mass
        total_inverse_mass = inv_mass1 + inv_mass2

        if distance == 0 or total_inverse_mass == 0:
            return

        direction = difference.normalize()

        error = distance - self.length
        
        correction = direction * error

        self.body1.position += correction * (inv_mass1/total_inverse_mass)
        self.body2.position -= correction * (inv_mass2/total_inverse_mass)