from enum import Enum

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    WHITE = 'white'
    BLACK = 'black'

class CustomCoercers:
    @staticmethod
    def parse_vector(s):
        parts = s.split(',')
        return tuple(float(p) for p in parts)

    @staticmethod
    def parse_color(s):
        key = s.strip().lower()
        for c in Color:
            if c.value == key:
                return c
        raise ValueError(f"Unknown color: {s}")

    @staticmethod
    def parse_duration(s):
        s = s.strip().lower()
        if s.endswith('ms'):
            return float(s[:-2]) / 1000.0
        elif s.endswith('s'):
            return float(s[:-1])
        elif s.endswith('m'):
            return float(s[:-1]) * 60.0
        else:
            return float(s)
