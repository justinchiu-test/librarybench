"""
Prompt styling with ANSI escape codes for translator.
"""
class PromptStyle:
    """
    Provides styling for prompts.
    """
    _codes = {
        'black': '30',
        'red': '91',
        'green': '92',
        'yellow': '93',
        'blue': '94',
        'magenta': '95',
        'cyan': '96',
        'white': '97',
    }

    @classmethod
    def style(cls, text, color):
        code = cls._codes.get(color)
        if not code:
            raise ValueError(f"Unknown color: {color}")
        return f"\033[{code}m{text}\033[0m"