from physics.body import Body


class BodyPool:

    def __init__(self, max_size=256):

        self.max_size = max_size

        self._available = []
        self._available_ids = set()

        self.created_count = 0
        self.reused_count = 0

    def acquire(
        self,
        x,
        y,
        radius=20,
        density=0.002,
        color=(255, 255, 255),
        is_static=False
    ):

        if self._available:

            body = self._available.pop()
            self._available_ids.remove(id(body))

            # Remove custom attributes from its previous life.
            body.__dict__.clear()

            # Reinitialize this existing Body instance.
            Body.__init__(
                body,
                x,
                y,
                radius=radius,
                density=density,
                color=color,
                is_static=is_static
            )

            self.reused_count += 1

        else:

            body = Body(
                x,
                y,
                radius=radius,
                density=density,
                color=color,
                is_static=is_static
            )

            self.created_count += 1

        return body

    def release(self, body):

        body_key = id(body)

        # Avoid inserting the same instance twice.
        if body_key in self._available_ids:
            return False

        # Do not let the inactive pool grow indefinitely.
        if len(self._available) >= self.max_size:
            return False

        self._available.append(body)
        self._available_ids.add(body_key)

        return True

    @property
    def available_count(self):
        return len(self._available)