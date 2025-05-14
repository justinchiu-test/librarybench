class WizardLayout:
    def __init__(self, pages):
        """
        pages: list of pages, each page is list of field names
        """
        self.pages = pages
        self.current = 0

    def get_current_page(self):
        return self.pages[self.current]

    def next_page(self):
        if self.current < len(self.pages) - 1:
            self.current += 1
        return self.get_current_page()

    def prev_page(self):
        if self.current > 0:
            self.current -= 1
        return self.get_current_page()
