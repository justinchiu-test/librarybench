import os
from enum import Enum

class HighLevelEventType(Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"

class HighLevelEventDetection:
    def detect(self, raw_event: dict) -> dict:
        etype = raw_event.get('event_type')
        if etype == 'created':
            ev = HighLevelEventType.CREATE
        elif etype == 'modified':
            ev = HighLevelEventType.MODIFY
        elif etype == 'deleted':
            ev = HighLevelEventType.DELETE
        elif etype == 'moved':
            ev = HighLevelEventType.MOVE
        else:
            ev = None
        return {
            'type': ev,
            'src_path': raw_event.get('src_path'),
            'dest_path': raw_event.get('dest_path')
        }
