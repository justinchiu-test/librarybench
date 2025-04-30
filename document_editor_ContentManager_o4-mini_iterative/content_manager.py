import uuid
import copy
import os

class Commit:
    def __init__(self, id, message, sections, locks):
        self.id = id
        self.message = message
        # deep copy to freeze state
        self.sections = copy.deepcopy(sections)
        self.locks = set(locks)

class Branch:
    def __init__(self, name, commits=None, sections=None, locks=None, tags=None):
        self.name = name
        # clone commits if provided
        if commits is None:
            self.commits = []
        else:
            # deep clone commits
            self.commits = [Commit(c.id, c.message, c.sections, c.locks) for c in commits]
        # clone sections
        self.sections = {} if sections is None else copy.deepcopy(sections)
        # clone locks
        self.locks = set() if locks is None else set(locks)
        # clone tags
        self.tags = {} if tags is None else dict(tags)

    def head(self):
        if not self.commits:
            return None
        return self.commits[-1]

class ContentManager:
    """
    A simple version control system for managing document content.
    """

    def __init__(self):
        # initialize with a 'main' branch
        self.branches = {'main': Branch('main')}
        self.current_branch = 'main'
        # collaborators set
        self.collaborators = set()
        # templates store: name -> (header, footer)
        self.templates = {}

    def switch_branch(self, name):
        """
        Switch the active branch to `name`.
        """
        if name not in self.branches:
            raise ValueError(f"Branch '{name}' not found")
        self.current_branch = name

    def branch(self, name):
        """
        Fork the current branch into a new branch called `name`.
        """
        if name in self.branches:
            raise ValueError(f"Branch '{name}' already exists")
        current = self.branches[self.current_branch]
        # clone branch state and history
        self.branches[name] = Branch(
            name,
            commits=current.commits,
            sections=current.sections,
            locks=current.locks,
            tags=current.tags
        )
        return name

    def commit(self, message):
        """
        Commit the current state of the document with a descriptive message.
        Returns the commit ID.
        """
        branch = self.branches[self.current_branch]
        cid = uuid.uuid4().hex
        commit = Commit(cid, message, branch.sections, branch.locks)
        branch.commits.append(commit)
        return cid

    def log(self):
        """
        Return the commit history for the current branch as a list of (id, message).
        """
        branch = self.branches[self.current_branch]
        return [(c.id, c.message) for c in branch.commits]

    def checkout(self, id_or_label):
        """
        Revert the working copy to a previous commit by ID or snapshot label.
        Returns the commit ID checked out.
        """
        branch = self.branches[self.current_branch]
        # find commit by ID
        commit = next((c for c in branch.commits if c.id == id_or_label), None)
        # if not found, try label lookup
        if commit is None:
            cid = branch.tags.get(id_or_label)
            if cid:
                commit = next((c for c in branch.commits if c.id == cid), None)
        if commit is None:
            raise ValueError("Commit or label not found")
        # restore state
        branch.sections = copy.deepcopy(commit.sections)
        branch.locks = set(commit.locks)
        return commit.id

    def snapshot(self, label):
        """
        Tag the current HEAD commit with a human-readable label.
        Returns the commit ID labeled.
        """
        branch = self.branches[self.current_branch]
        head = branch.head()
        if head is None:
            raise ValueError("No commits to snapshot")
        branch.tags[label] = head.id
        return head.id

    def merge(self, source, destination):
        """
        Naively merge changes from source branch into destination branch.
        Overwrites sections in destination with source's HEAD content unless locked.
        """
        if source not in self.branches or destination not in self.branches:
            raise ValueError("Branch not found")
        src = self.branches[source]
        dest = self.branches[destination]
        src_head = src.head()
        if src_head is None:
            # nothing to merge
            return
        for section, content in src_head.sections.items():
            if section in dest.locks:
                continue
            dest.sections[section] = content

    def import_content(self, file_path, section_name=None):
        """
        Import content from an external file into a new or existing section.
        If section_name is None, uses the basename of the file.
        Returns the section name created/updated.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError("File not found")
        name = section_name or os.path.basename(file_path)
        branch = self.branches[self.current_branch]
        if name in branch.locks:
            raise ValueError("Section is locked")
        with open(file_path, 'r') as f:
            content = f.read()
        branch.sections[name] = content
        return name

    def create_template(self, tpl_name, header, footer):
        """
        Define a new template with header and footer.
        """
        if tpl_name in self.templates:
            raise ValueError("Template already exists")
        self.templates[tpl_name] = (header, footer)

    def apply_template(self, tpl_name, section_name):
        """
        Apply a named template to a section, wrapping its content.
        """
        if tpl_name not in self.templates:
            raise ValueError("Template not found")
        branch = self.branches[self.current_branch]
        if section_name not in branch.sections:
            raise ValueError("Section not found")
        if section_name in branch.locks:
            raise ValueError("Section is locked")
        header, footer = self.templates[tpl_name]
        content = branch.sections[section_name]
        branch.sections[section_name] = f"{header}{content}{footer}"

    def collaborator_list(self):
        """
        Return the list of collaborators.
        """
        return list(self.collaborators)

    def add_collaborator(self, name):
        """
        Add a collaborator by name.
        """
        self.collaborators.add(name)

    def remove_collaborator(self, name):
        """
        Remove a collaborator by name.
        """
        if name not in self.collaborators:
            raise ValueError("Collaborator not found")
        self.collaborators.remove(name)

    def lock_section(self, section_name):
        """
        Lock a section to prevent edits.
        """
        branch = self.branches[self.current_branch]
        if section_name not in branch.sections:
            raise ValueError("Section not found")
        branch.locks.add(section_name)
