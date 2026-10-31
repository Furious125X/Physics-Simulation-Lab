class AABBNode:

    def __init__(
        self,
        bounds=None,
        body=None,
        left=None,
        right=None
    ):

        self.reset(
            bounds,
            body,
            left,
            right
        )

    def reset(
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

        return (
            self.left is None
            and self.right is None
        )


class AABBTree:

    def __init__(self, max_pool_size=None):

        self.root = None
        self.body_count = 0

        self.node_pool = []

        self.max_pool_size = max_pool_size

        self.created_node_count = 0
        self.reused_node_count = 0

        self.active_node_count = 0

    @property
    def pooled_node_count(self):
        return len(self.node_pool)

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

        # Recycle nodes from the previous tree.
        self.recycle_tree()

        entries = list(proxies)

        self.body_count = len(entries)

        if not entries:
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

            return self.acquire_node(
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

        return self.acquire_node(
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


    def acquire_node(
        self,
        bounds,
        body=None,
        left=None,
        right=None
    ):

        if self.node_pool:

            node = self.node_pool.pop()

            node.reset(
                bounds,
                body,
                left,
                right
            )

            self.reused_node_count += 1

        else:

            node = AABBNode(
                bounds,
                body,
                left,
                right
            )

            self.created_node_count += 1

        self.active_node_count += 1

        return node


    def recycle_tree(self):

        if self.root is None:
            self.active_node_count = 0
            return

        stack = [self.root]

        while stack:

            node = stack.pop()

            # Save child references before resetting.
            left = node.left
            right = node.right

            if left is not None:
                stack.append(left)

            if right is not None:
                stack.append(right)

            # Remove references to the previous tree.
            node.reset(None)

            # Store the node if pool capacity allows.
            if (
                self.max_pool_size is None
                or len(self.node_pool) < self.max_pool_size
            ):

                self.node_pool.append(node)

        self.root = None
        self.active_node_count = 0


    