class AABBNode:

    def __init__(
        self,
        bounds,
        body=None,
        left=None,
        right=None
    ):

        self.bounds = bounds
        self.body = body
        self.left = left
        self.right = right

    @property
    def is_leaf(self):
        return self.left is None and self.right is None


class AABBTree:

    def __init__(self):
        self.root = None
        self.body_count = 0

    @staticmethod
    def combine(bounds1, bounds2):

        return (
            min(bounds1[0], bounds2[0]),
            min(bounds1[1], bounds2[1]),
            max(bounds1[2], bounds2[2]),
            max(bounds1[3], bounds2[3])
        )

    @staticmethod
    def overlaps(bounds1, bounds2):

        return not (
            bounds1[2] < bounds2[0]
            or bounds1[0] > bounds2[2]
            or bounds1[3] < bounds2[1]
            or bounds1[1] > bounds2[3]
        )

    def build(self, proxies):

        entries = list(proxies)

        self.body_count = len(entries)

        if not entries:
            self.root = None
            return

        self.root = self._build_node(entries)

    def _build_node(self, entries):

        bounds = entries[0][1]

        for _, other_bounds in entries[1:]:

            bounds = self.combine(
                bounds,
                other_bounds
            )

        # A single body becomes a leaf.
        if len(entries) == 1:

            body, body_bounds = entries[0]

            return AABBNode(
                body_bounds,
                body=body
            )

        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # Split along the longest axis.
        if width >= height:

            entries.sort(
                key=lambda item: (
                    item[1][0] + item[1][2]
                ) / 2
            )

        else:

            entries.sort(
                key=lambda item: (
                    item[1][1] + item[1][3]
                ) / 2
            )

        midpoint = len(entries) // 2

        left = self._build_node(
            entries[:midpoint]
        )

        right = self._build_node(
            entries[midpoint:]
        )

        return AABBNode(
            self.combine(
                left.bounds,
                right.bounds
            ),
            left=left,
            right=right
        )

    def query(self, bounds):

        results = []

        if self.root is None:
            return results

        stack = [self.root]

        while stack:

            node = stack.pop()

            if not self.overlaps(
                node.bounds,
                bounds
            ):
                continue

            if node.is_leaf:

                results.append(node.body)

            else:

                stack.append(node.left)
                stack.append(node.right)

        return results