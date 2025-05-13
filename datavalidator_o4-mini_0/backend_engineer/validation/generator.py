import random
import string

class TestDataGenerator:
    TYPE_MAP = {
        int: lambda: random.randint(0, 100),
        float: lambda: random.random() * 100,
        bool: lambda: random.choice([True, False]),
        str: lambda: ''.join(random.choices(string.ascii_lowercase, k=8)),
    }

    @classmethod
    def generate(cls, schema):
        data = {}
        for name, field in schema.fields.items():
            t = field.type_
            gen = cls.TYPE_MAP.get(t, lambda: None)
            data[name] = gen()
        return data
