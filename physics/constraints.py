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

        if distance == 0:
            return

        direction = difference.normalize()

        error = distance - self.length

        correction = direction * (error / 2)

        self.body1.position += correction
        self.body2.position -= correction