class DistanceConstraint:
    def __init__(self, body, anchor, lenght):
        self.body = body
        self.anchor = anchor
        self.lenght = lenght


    def solve(self):
        difference = self.body.position - self.anchor
        if difference.length == 0:
            return
        direction = difference.normalize()
        self.body.position = self.anchor + direction * self.lenght