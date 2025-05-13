class FileSystemEventHandler:
    # dummy base
    pass

class FileSystemEvent:
    def __init__(self, src_path):
        self.src_path = src_path

class FileCreatedEvent(FileSystemEvent):
    pass

class FileModifiedEvent(FileSystemEvent):
    pass

class FileDeletedEvent(FileSystemEvent):
    pass

class FileMovedEvent(FileSystemEvent):
    def __init__(self, src_path, dest_path):
        super().__init__(src_path)
        self.dest_path = dest_path
