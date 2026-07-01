class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector2(
            self.x + other.x,
            self.y + other.y
        )

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __mul__(self, scalar):
        return Vector2(
            self.x * scalar,
            self.y * scalar
        )
    
    def __sub__(self, other):
        return Vector2(
            self.x - other.x,
            self.y - other.y
        )
    
    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def __repr__(self):
        return f"Vector2({self.x:.2f}, {self.y:.2f})"
    
    def length_squared(self):
        return self.x * self.x + self.y * self.y
    
    def normalize(self):
        length = self.length()

        if length == 0:
            return Vector2()

        return Vector2(
            self.x / length,
            self.y / length
        )
    
    def __truediv__(self, scalar):
        return Vector2(
            self.x / scalar,
            self.y / scalar
        )
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y