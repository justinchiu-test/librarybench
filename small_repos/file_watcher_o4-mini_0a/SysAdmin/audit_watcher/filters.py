import os

class HiddenFileFilter:
    """
    Filter for hidden files based on mode:
      - "exclude": hide files beginning with '.'
      - "only": only include files beginning with '.'
      - "all": include all files
    """
    VALID_MODES = ("exclude", "only", "all")

    def __init__(self, mode: str):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid hidden-file mode: {mode}")
        self.mode = mode

    def filter(self, event) -> bool:
        name = os.path.basename(event.src_path)
        is_hidden = name.startswith('.')
        if self.mode == "exclude":
            return not is_hidden
        if self.mode == "only":
            return is_hidden
        # "all"
        return True
