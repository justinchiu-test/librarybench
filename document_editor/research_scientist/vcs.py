import copy
import difflib


class Commit:
    def __init__(self, id_, message, parents, snapshot):
        self.id = id_
        self.message = message
        self.parents = parents  # list of parent Commits
        # snapshot is a dict: filename -> content string
        self.snapshot = copy.deepcopy(snapshot)

    def __repr__(self):
        parent_ids = [p.id for p in self.parents]
        return f"<Commit {self.id} parents={parent_ids} msg={self.message!r}>"


class Branch:
    def __init__(self, name, head_commit):
        self.name = name
        self.head = head_commit

    def __repr__(self):
        return f"<Branch {self.name} head={self.head.id}>"


class Repository:
    def __init__(self):
        # store commits by id
        self.commits = {}
        # store branches by name
        self.branches = {}
        # store tags by name -> Commit
        self.tags = {}
        # id counter
        self._next_id = 1

        # Initialize with an initial empty commit
        initial = Commit("0", "initial commit", [], {})
        self.commits[initial.id] = initial
        main_branch = Branch("main", initial)
        self.branches[main_branch.name] = main_branch

        self.current_branch = main_branch
        self.HEAD = initial
        # working directory: filename -> content
        self.working_directory = {}

    def _generate_id(self):
        cid = str(self._next_id)
        self._next_id += 1
        return cid

    def branch(self, name):
        """Create a new branch at current HEAD."""
        if name in self.branches:
            raise ValueError(f"Branch '{name}' already exists")
        new_branch = Branch(name, self.HEAD)
        self.branches[name] = new_branch
        return new_branch

    def checkout(self, name):
        """Switch to branch or tag."""
        if name in self.branches:
            br = self.branches[name]
            self.current_branch = br
            self.HEAD = br.head
            # reset working directory to HEAD snapshot
            self.working_directory = copy.deepcopy(self.HEAD.snapshot)
        elif name in self.tags:
            commit = self.tags[name]
            self.HEAD = commit
            # working directory updated, but branch stays the same
            self.working_directory = copy.deepcopy(commit.snapshot)
        else:
            raise ValueError(f"No branch or tag named '{name}'")

    def commit(self, message):
        """Commit current working directory."""
        cid = self._generate_id()
        parents = [self.HEAD]
        snapshot = self.working_directory
        new_commit = Commit(cid, message, parents, snapshot)
        self.commits[cid] = new_commit
        # update HEAD and branch head
        self.HEAD = new_commit
        self.current_branch.head = new_commit
        return new_commit

    def edit(self, filename, new_content, append=False):
        """Edit a file in working directory."""
        if append and filename in self.working_directory:
            self.working_directory[filename] += new_content
        else:
            self.working_directory[filename] = new_content

    def revert(self):
        """Revert to previous commit on current branch."""
        parent = None
        if self.HEAD.parents:
            parent = self.HEAD.parents[0]
        if parent is None:
            # nothing to revert
            return
        # move branch head
        self.current_branch.head = parent
        self.HEAD = parent
        self.working_directory = copy.deepcopy(parent.snapshot)

    def comment(self, filename, comment_text, position="top"):
        """Insert a comment line into a file."""
        if filename not in self.working_directory:
            raise ValueError(f"File '{filename}' does not exist")
        content = self.working_directory[filename]
        comment_line = f"# {comment_text}\n"
        if position == "top":
            new_content = comment_line + content
        elif position == "bottom":
            new_content = content + comment_line
        else:
            raise ValueError("position must be 'top' or 'bottom'")
        self.working_directory[filename] = new_content

    def search(self, query):
        """Search for a query in working directory, return list of (file, line_no, line)."""
        results = []
        for fname, content in self.working_directory.items():
            for idx, line in enumerate(content.splitlines(), start=1):
                if query in line:
                    results.append((fname, idx, line))
        return results

    def snapshot(self, tag_name):
        """Tag current HEAD with a snapshot tag."""
        if tag_name in self.tags:
            raise ValueError(f"Tag '{tag_name}' already exists")
        self.tags[tag_name] = self.HEAD

    def _find_common_ancestor(self, commit1, commit2):
        """Find a common ancestor by walking parents (naive)."""
        ancestors1 = set()
        stack = [commit1]
        while stack:
            c = stack.pop()
            ancestors1.add(c.id)
            for p in c.parents:
                if p.id not in ancestors1:
                    stack.append(p)
        # walk commit2
        stack = [commit2]
        while stack:
            c = stack.pop()
            if c.id in ancestors1:
                return c
            for p in c.parents:
                stack.append(p)
        return None

    def merge(self, branch_name):
        """Merge another branch into current branch."""
        if branch_name not in self.branches:
            raise ValueError(f"No branch named '{branch_name}'")
        other_branch = self.branches[branch_name]
        ours = self.HEAD
        theirs = other_branch.head
        base = self._find_common_ancestor(ours, theirs)
        if base is None:
            base = Commit("empty", "", [], {})

        merged = {}
        # collect all filenames
        files = set(base.snapshot) | set(ours.snapshot) | set(theirs.snapshot)
        for f in files:
            b = base.snapshot.get(f, "")
            o = ours.snapshot.get(f, "")
            t = theirs.snapshot.get(f, "")
            if o == t:
                merged[f] = o
            elif o == b:
                merged[f] = t
            elif t == b:
                merged[f] = o
            else:
                # conflict
                merged[f] = (
                    f"<<<<<<< HEAD\n{o}=======\n{t}>>>>>>> {branch_name}\n"
                )
        # update working directory
        self.working_directory = merged
        # make merge commit with two parents
        cid = self._generate_id()
        message = f"Merge branch {branch_name} into {self.current_branch.name}"
        new_commit = Commit(cid, message, [ours, theirs], merged)
        self.commits[cid] = new_commit
        self.HEAD = new_commit
        self.current_branch.head = new_commit
        return new_commit

    def diff(self, a=None, b=None):
        """
        Diff between two commits or working directory.
        a, b can be commit IDs or None (means working dir for b, HEAD for a).
        Returns unified diff as list of lines.
        """
        # Helper to get snapshot by id or working dir
        def get_snap(x):
            if x is None:
                return self.working_directory
            if x in self.commits:
                return self.commits[x].snapshot
            raise ValueError(f"Unknown commit '{x}'")

        if a is None:
            a = self.HEAD.id
        if b is None:
            # working dir
            snap_a = get_snap(a)
            snap_b = self.working_directory
        else:
            snap_a = get_snap(a)
            snap_b = get_snap(b)

        diffs = []
        # for each file in either
        files = sorted(set(snap_a) | set(snap_b))
        for f in files:
            a_lines = snap_a.get(f, "").splitlines(keepends=True)
            b_lines = snap_b.get(f, "").splitlines(keepends=True)
            if a_lines != b_lines:
                header = f"--- {a}/{f}\n+++ {b or 'working'}/{f}\n"
                diffs.append(header)
                for line in difflib.unified_diff(a_lines, b_lines, lineterm=""):
                    diffs.append(line + "\n")
        return diffs
