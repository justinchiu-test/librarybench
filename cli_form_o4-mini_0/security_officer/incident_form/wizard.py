class WizardLayout:
    def __init__(self, pages):
        if not pages or not isinstance(pages, list):
            raise ValueError("Pages must be a non-empty list")
        self.pages = pages
        self.current = 0

    def next_page(self):
        if self.current < len(self.pages) - 1:
            self.current += 1
        return self.get_current_page()

    def prev_page(self):
        if self.current > 0:
            self.current -= 1
        return self.get_current_page()

    def get_current_page(self):
        return self.pages[self.current]
