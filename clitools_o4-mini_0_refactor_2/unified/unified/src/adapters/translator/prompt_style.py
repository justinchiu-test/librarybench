"""
Prompt styling for Translator CLI adapter.
"""
class PromptStyle:
    colors = {
        'red': '\033[91m',
        # additional colors can be added
    }
    reset = '\033[0m'

    @staticmethod
    def style(text, color):
        start = PromptStyle.colors.get(color, '')
        return f"{start}{text}{PromptStyle.reset}"