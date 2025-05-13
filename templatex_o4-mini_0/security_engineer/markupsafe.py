# Simple stub so tests importing markupsafe.Markup will succeed.
# Markup is just a string subclass.
class Markup(str):
    def __new__(cls, text):
        return super(Markup, cls).__new__(cls, text)
    def __html__(self):
        # mimic Markup interface
        return self
