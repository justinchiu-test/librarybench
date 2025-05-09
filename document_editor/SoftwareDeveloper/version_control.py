from copy import deepcopy

class Repo:
    def __init__(self):
        self.files = {}  # path -> content
        self.branches = {'main': []}  # branch_name -> list of commits
        self.current_branch = 'main'
        self.head = -1  # index into branches[current_branch]
        self.collaborators = set()
        # locked_sections[file] = set of section_ids that are locked
        self.locked_sections = {}
        # name -> template string
        self.templates = {}
        # stack of undone commits for redo
        self._undo_stack = []

    def commit(self, message):
        # snapshot current files
        snapshot = deepcopy(self.files)
        commit_id = f"{self.current_branch}-{len(self.branches[self.current_branch])}"
        commit = {'id': commit_id, 'message': message, 'snapshot': snapshot}
        # if we had undone some commits, drop any "future" commits
        self.branches[self.current_branch] = self.branches[self.current_branch][:self.head+1]
        self.branches[self.current_branch].append(commit)
        self.head += 1
        # clear redo stack once new commit is made
        self._undo_stack.clear()
        return commit_id

    def undo(self):
        if self.head < 0:
            raise Exception("Nothing to undo")
        commit = self.branches[self.current_branch][self.head]
        self._undo_stack.append(commit)
        # remove the last commit
        self.branches[self.current_branch] = self.branches[self.current_branch][:self.head]
        self.head -= 1
        # restore files
        if self.head >= 0:
            self.files = deepcopy(self.branches[self.current_branch][self.head]['snapshot'])
        else:
            self.files = {}
        return commit['id']

    def redo(self):
        if not self._undo_stack:
            raise Exception("Nothing to redo")
        commit = self._undo_stack.pop()
        self.branches[self.current_branch].append(commit)
        self.head += 1
        self.files = deepcopy(commit['snapshot'])
        return commit['id']

    def lock_section(self, file, section_id):
        """Lock a section so that edit(file, ..., section_id) will raise."""
        self.locked_sections.setdefault(file, set()).add(section_id)

    def unlock_section(self, file, section_id):
        # unlock removes the section_id from locked_sections[file]
        if file in self.locked_sections:
            self.locked_sections[file].discard(section_id)

    def edit(self, file, content, section_id=None):
        # if editing a section, ensure it's unlocked
        if section_id is not None:
            locked = self.locked_sections.get(file, set())
            if section_id in locked:
                raise Exception(f"Section {section_id} locked in {file}")
        self.files[file] = content

    def collaborator_list(self):
        return list(sorted(self.collaborators))

    def add_collaborator(self, name):
        self.collaborators.add(name)

    def remove_collaborator(self, name):
        self.collaborators.discard(name)

    def history_view(self):
        return [c['message'] for c in self.branches[self.current_branch]]

    def apply_operation(self, operation):
        # return a new Repo object with the op applied, original unchanged
        new_repo = deepcopy(self)
        operation(new_repo)
        return new_repo

    def resolve_conflict(self, file):
        # keep "ours" part of a conflict:
        # <<<<<<<
        # ... ours lines ...
        # =======
        # ... theirs lines ...
        # >>>>>>>
        text = self.files.get(file, "")
        lines = text.splitlines()
        result = []
        side = None  # None=normal, 'ours', 'theirs'
        for ln in lines:
            if ln.startswith("<<<<<<<"):
                side = 'ours'
                continue
            if ln.startswith("=======") and side == 'ours':
                side = 'theirs'
                continue
            if ln.startswith(">>>>>>>") and side == 'theirs':
                side = None
                continue
            if side == 'theirs':
                continue
            # if side==ours or side==None
            result.append(ln)
        self.files[file] = "\n".join(result)

    def template_support(self, name, template=None):
        if template is not None:
            self.templates[name] = template
        return self.templates.get(name)

    def branch(self, name):
        if name in self.branches:
            raise Exception(f"Branch {name} already exists")
        # copy commits up to head
        commits = deepcopy(self.branches[self.current_branch][:self.head+1])
        self.branches[name] = commits

    def checkout(self, target):
        # if branch
        if target in self.branches:
            self.current_branch = target
            self.head = len(self.branches[target]) - 1
            if self.head >= 0:
                self.files = deepcopy(self.branches[target][self.head]['snapshot'])
            else:
                self.files = {}
            self._undo_stack.clear()
            return
        # if commit id in current branch
        for idx, c in enumerate(self.branches[self.current_branch]):
            if c['id'] == target:
                self.head = idx
                self.files = deepcopy(c['snapshot'])
                self._undo_stack.clear()
                return
        raise Exception(f"Unknown branch or commit: {target}")


# module‐level wrappers:

def lock_section(repo, file, section_id):
    return repo.lock_section(file, section_id)

def unlock_section(repo, file, section_id):
    return repo.unlock_section(file, section_id)

def edit(repo, file, content, section_id=None):
    return repo.edit(file, content, section_id)

def collaborator_list(repo):
    return repo.collaborator_list()

def add_collaborator(repo, name):
    return repo.add_collaborator(name)

def remove_collaborator(repo, name):
    return repo.remove_collaborator(name)

def history_view(repo):
    return repo.history_view()

def apply_operation(repo, operation):
    return repo.apply_operation(operation)

def resolve_conflict(repo, file):
    return repo.resolve_conflict(file)

def template_support(repo, name, template=None):
    return repo.template_support(name, template)

def branch(repo, name):
    return repo.branch(name)

def checkout(repo, target):
    return repo.checkout(target)

def redo(repo):
    return repo.redo()

def undo(repo):
    return repo.undo()

def commit(repo, message):
    return repo.commit(message)
