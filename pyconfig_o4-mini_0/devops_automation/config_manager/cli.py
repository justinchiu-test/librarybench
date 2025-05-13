class InteractiveCLI:
    def prompt(self, name, prompt_text, default=None):
        try:
            inp = input(f"{prompt_text} [{default}]: ")
        except EOFError:
            inp = ''
        if inp.strip() == "":
            return default
        return inp
