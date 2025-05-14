class PromptStyle:
    """
    Simple ANSI-based prompt styling.
    """
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'end': '\033[0m'
    }

    @classmethod
    def style(cls, text, color):
        """
        Wrap text with ANSI color codes.
        """
        start = cls.COLORS.get(color, '')
        end = cls.COLORS['end']
        return f"{start}{text}{end}"
