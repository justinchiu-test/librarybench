import difflib
import datetime

class DocumentManager:
    def __init__(self, initial_content=''):
        self.content = initial_content
        self.versions = {0: initial_content}
        self.current_version = 0
        self.snapshots = {}
        self.collaborators = set()
        self.comments = {}            # section -> list of (user, comment)
        self.locked_sections = set()
        self.activity_feed_list = []
        self.notifications_dict = {}  # user -> list of messages
        self.operations_queue = []
        self.commit_log = []
        self.conflicts = {}

    def _add_activity(self, action, details=''):
        timestamp = datetime.datetime.utcnow().isoformat()
        entry = f"{timestamp}: {action} {details}".strip()
        self.activity_feed_list.append(entry)

    def _notify_all(self, message):
        for user in self.collaborators:
            self.notifications_dict.setdefault(user, []).append(message)

    def resolve_conflict(self, key, resolved_value):
        self.conflicts[key] = resolved_value
        self._add_activity('resolve_conflict', f'{key}={resolved_value}')
        self.commit_log.append(f'resolve_conflict {key}={resolved_value}')
        return True

    def collaborator_list(self):
        return list(self.collaborators)

    def add_collaborator(self, user):
        self.collaborators.add(user)
        self.notifications_dict.setdefault(user, [])
        self._add_activity('add_collaborator', user)
        self.commit_log.append(f'add_collaborator {user}')

    def remove_collaborator(self, user):
        if user in self.collaborators:
            self.collaborators.remove(user)
            self.notifications_dict.pop(user, None)
            self._add_activity('remove_collaborator', user)
            self.commit_log.append(f'remove_collaborator {user}')
            return True
        return False

    def activity_feed(self):
        return list(self.activity_feed_list)

    def comment(self, section, user, comment_text):
        if user not in self.collaborators:
            raise ValueError("User not a collaborator")
        self.comments.setdefault(section, []).append((user, comment_text))
        self._add_activity('comment', f'{user}@{section}: {comment_text}')
        self.commit_log.append(f'comment {user}@{section}: {comment_text}')
        self._notify_all(f"{user} commented on {section}: {comment_text}")

    def lock_section(self, section):
        self.locked_sections.add(section)
        self._add_activity('lock_section', section)
        self.commit_log.append(f'lock_section {section}')

    def unlock_section(self, section):
        if section in self.locked_sections:
            self.locked_sections.remove(section)
            self._add_activity('unlock_section', section)
            self.commit_log.append(f'unlock_section {section}')
            return True
        return False

    def snapshot(self, label):
        self.snapshots[label] = self.current_version
        self._add_activity('snapshot', f'{label}@{self.current_version}')
        self.commit_log.append(f'snapshot {label}@{self.current_version}')

    def version_compare(self, version1, version2):
        c1 = self.versions.get(version1)
        c2 = self.versions.get(version2)
        if c1 is None or c2 is None:
            raise ValueError("Version not found")
        diff = list(difflib.unified_diff(
            c1.splitlines(), c2.splitlines(),
            fromfile=f'v{version1}', tofile=f'v{version2}', lineterm=''
        ))
        self._add_activity('version_compare', f'{version1} vs {version2}')
        return diff

    def notifications(self, user=None):
        if user:
            return list(self.notifications_dict.get(user, []))
        return {u: list(msgs) for u, msgs in self.notifications_dict.items()}

    def apply_operation(self, operation):
        # keep the pre-op content around for edit slicing
        original_content = self.content
        self.operations_queue.append(operation)
        op_type = operation.get('type')
        pos = operation.get('position', 0)

        if op_type == 'insert':
            text = operation.get('text', '')
            self.content = original_content[:pos] + text + original_content[pos:]
            details = f"insert '{text}' at {pos}"

        elif op_type == 'delete':
            length = operation.get('length', 0)
            self.content = original_content[:pos] + original_content[pos+length:]
            details = f"delete {length} chars at {pos}"

        elif op_type == 'edit':
            length = operation.get('length', 0)
            text = operation.get('text', '')

            before = original_content[:pos]
            if length > 0:
                # slice trailing start at pos + length - 1 so that we leave the last char in place
                tail_index = pos + length - 1
            else:
                tail_index = pos
            # clamp the tail index
            if tail_index < 0:
                tail_index = 0
            if tail_index > len(original_content):
                tail_index = len(original_content)

            tail = original_content[tail_index:]
            self.content = before + text + tail
            details = f"edit {length} chars at {pos} with '{text}'"

        else:
            raise ValueError("Unknown operation type")

        # Update versioning
        self.current_version += 1
        self.versions[self.current_version] = self.content

        # Record activity and log
        self._add_activity('apply_operation', details)
        self.commit_log.append(f'apply_operation {details}')

        # Notify collaborators
        self._notify_all(f"Operation applied: {details}")
        return True

    def log(self):
        return list(self.commit_log)
