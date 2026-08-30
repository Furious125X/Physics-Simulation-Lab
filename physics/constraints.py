from physics.vector import Vector2


class AnchorConstraint:
    def __init__(self, body, anchor, length, compliance=0.0):
        self.body = body
        self.anchor = anchor
        self.length = length
        self.compliance = compliance
        self.lambda_accum = 0.0

    def solve(self, dt):
        difference = self.body.position - self.anchor
        distance = difference.length()

        if distance == 0:
            return

        inv_mass = self.body.inverse_mass
        if inv_mass == 0:
            return

        direction = difference / distance
        C = distance - self.length

        if abs(C) < 0.01:
            return

        alpha = self.compliance / (dt * dt)
        delta_lambda = (C - alpha * self.lambda_accum) / (inv_mass + alpha)
        self.lambda_accum += delta_lambda

        self.body.position -= direction * delta_lambda * inv_mass

    def begin_substep(self):
        self.lambda_accum = 0.0


class DistanceConstraint:
    def __init__(self, body1, body2, length, stiffness=1.0, compliance=0.0):
        self.body1 = body1
        self.body2 = body2
        self.length = length
        self.stiffness = stiffness
        self.compliance = compliance
        self.lambda_accum = 0.0

    def solve(self, dt):
        difference = self.body2.position - self.body1.position
        distance = difference.length()

        inv_mass1 = self.body1.inverse_mass
        inv_mass2 = self.body2.inverse_mass
        total_inverse_mass = inv_mass1 + inv_mass2

        if distance == 0 or total_inverse_mass == 0:
            return

        direction = difference / distance
        C = distance - self.length

        if abs(C) < 0.01:
            return

        alpha = self.compliance / (dt * dt)
        delta_lambda = (C - alpha * self.lambda_accum) / (total_inverse_mass + alpha)
        self.lambda_accum += delta_lambda

        self.body1.position += direction * delta_lambda * inv_mass1
        self.body2.position -= direction * delta_lambda * inv_mass2

    def begin_substep(self):
        self.lambda_accum = 0.0


class AtwoodConstraint:

    def __init__(
        self,
        body1,
        body2,
        pulley,
        rope_length,
        compliance=0.0
    ):
        self.body1 = body1
        self.body2 = body2
        self.pulley = pulley
        self.rope_length = rope_length
        self.compliance = compliance
        self.lambda_accum = 0.0

    def solve(self, dt):

        difference1 = self.body1.position - self.pulley
        difference2 = self.body2.position - self.pulley

        distance1 = difference1.length()
        distance2 = difference2.length()

        if distance1 == 0 or distance2 == 0:
            return

        inv_mass1 = self.body1.inverse_mass
        inv_mass2 = self.body2.inverse_mass

        total_inverse_mass = (
            inv_mass1
            + inv_mass2
        )

        if total_inverse_mass == 0:
            return

        direction1 = difference1 / distance1
        direction2 = difference2 / distance2

        C = (
            distance1
            + distance2
            - self.rope_length
        )

        if abs(C) < 0.01:
            return

        alpha = (
            self.compliance
            / (dt * dt)
        )

        delta_lambda = (
            C
            - alpha * self.lambda_accum
        ) / (
            total_inverse_mass
            + alpha
        )

        self.lambda_accum += delta_lambda

        self.body1.position -= (
            direction1
            * delta_lambda
            * inv_mass1
        )

        self.body2.position -= (
            direction2
            * delta_lambda
            * inv_mass2
        )

    def begin_substep(self):
        self.lambda_accum = 0.0