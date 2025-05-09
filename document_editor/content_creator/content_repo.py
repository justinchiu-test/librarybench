import copy
from datetime import datetime

class Commit:
    def __init__(self, id, message, parents, state):
        self.id = id
        self.message = message
        self.parents = parents  # list of commit ids
        self.state = copy.deepcopy(state)  # deep snapshot of content
        self.timestamp = datetime.now()
        self.tags = set()

class ContentRepo:
    def __init__(self):
        self._commits = {}
        self._next_commit_id = 1
        # initial empty commit
        initial = Commit('0', 'Initial commit', [], {})
        self._commits['0'] = initial
        self.branches = {'main': '0'}
        self.head_branch = 'main'
        self.head_commit = '0'
        self.working_copy = copy.deepcopy(initial.state)
        self.tags = {}  # tag_name -> commit_id

    def commit(self, message):
        cid = str(self._next_commit_id)
        self._next_commit_id += 1
        parents = [self.head_commit]
        newc = Commit(cid, message, parents, self.working_copy)
        self._commits[cid] = newc
        # move branch head
        if self.head_branch:
            self.branches[self.head_branch] = cid
        self.head_commit = cid
        return cid

    def branch(self, branch_name, from_branch=None):
        if branch_name in self.branches:
            raise ValueError(f"Branch '{branch_name}' already exists")
        src = from_branch if from_branch is not None else self.head_branch
        if src not in self.branches:
            raise ValueError(f"Unknown branch '{src}'")
        self.branches[branch_name] = self.branches[src]

    def checkout(self, name):
        if name in self.branches:
            # checkout branch
            self.head_branch = name
            self.head_commit = self.branches[name]
        elif name in self._commits:
            # detached HEAD
            self.head_branch = None
            self.head_commit = name
        else:
            raise ValueError(f"Unknown branch or commit '{name}'")
        # reset working copy
        self.working_copy = copy.deepcopy(self._commits[self.head_commit].state)

    def edit(self, content_id, section, new_text):
        if content_id not in self.working_copy:
            self.working_copy[content_id] = {'sections': {}, 'comments': {}}
        cont = self.working_copy[content_id]
        cont['sections'][section] = new_text
        cont['comments'].setdefault(section, [])

    def comment(self, content_id, section, comment_text):
        if content_id not in self.working_copy:
            raise ValueError(f"Content '{content_id}' not found")
        cont = self.working_copy[content_id]
        if section not in cont['sections']:
            raise ValueError(f"Section '{section}' not found in content '{content_id}'")
        cont['comments'].setdefault(section, []).append(comment_text)

    def search(self, query):
        q = query.lower()
        found = []
        for cid, cont in self.working_copy.items():
            if q in cid.lower():
                found.append(cid)
                continue
            hit = False
            for sec, txt in cont['sections'].items():
                if q in sec.lower() or q in txt.lower():
                    hit = True
                    break
            if hit:
                found.append(cid)
                continue
            for comments in cont['comments'].values():
                if any(q in cm.lower() for cm in comments):
                    found.append(cid)
                    break
        return found

    def revert(self, content_id, commit_id):
        if commit_id not in self._commits:
            raise ValueError(f"Unknown commit '{commit_id}'")
        state = self._commits[commit_id].state
        if content_id not in state:
            raise ValueError(f"Content '{content_id}' not in commit '{commit_id}'")
        self.working_copy[content_id] = copy.deepcopy(state[content_id])

    def snapshot(self, tag_name, commit_id=None):
        cid = commit_id if commit_id is not None else self.head_commit
        if cid not in self._commits:
            raise ValueError(f"Unknown commit '{cid}'")
        if tag_name in self.tags:
            raise ValueError(f"Tag '{tag_name}' already exists")
        self.tags[tag_name] = cid
        self._commits[cid].tags.add(tag_name)

    def merge(self, source, target=None):
        if source not in self.branches:
            raise ValueError(f"Unknown source branch '{source}'")
        tgt = target if target is not None else self.head_branch
        if tgt is None or tgt not in self.branches:
            raise ValueError(f"Unknown target branch '{tgt}'")
        src_commit = self._commits[self.branches[source]]
        tgt_commit = self._commits[self.branches[tgt]]
        # start from target state
        merged = copy.deepcopy(tgt_commit.state)
        # overlay source state
        for cid, cont in src_commit.state.items():
            if cid not in merged:
                merged[cid] = copy.deepcopy(cont)
            else:
                # merge sections
                for sec, txt in cont['sections'].items():
                    merged[cid]['sections'][sec] = txt
                # merge comments
                for sec, cms in cont['comments'].items():
                    merged[cid]['comments'].setdefault(sec, []).extend(cms)
        # checkout target and commit the merge
        self.checkout(tgt)
        self.working_copy = merged
        mid = str(self._next_commit_id)
        self._next_commit_id += 1
        merge_msg = f"Merged {source} into {tgt}"
        newc = Commit(mid, merge_msg, [tgt_commit.id, src_commit.id], self.working_copy)
        self._commits[mid] = newc
        self.branches[tgt] = mid
        self.head_commit = mid
        return mid

    def diff(self, content_id, commit_id1, commit_id2):
        if commit_id1 not in self._commits or commit_id2 not in self._commits:
            raise ValueError("Unknown commit")
        s1 = self._commits[commit_id1].state.get(content_id, {'sections':{}, 'comments':{}})
        s2 = self._commits[commit_id2].state.get(content_id, {'sections':{}, 'comments':{}})
        diffs = {}
        # sections
        secs = set(s1['sections']) | set(s2['sections'])
        for sec in secs:
            t1 = s1['sections'].get(sec)
            t2 = s2['sections'].get(sec)
            if t1 != t2:
                diffs.setdefault('sections', {})[sec] = (t1, t2)
        # comments
        csecs = set(s1['comments']) | set(s2['comments'])
        for sec in csecs:
            cm1 = s1['comments'].get(sec, [])
            cm2 = s2['comments'].get(sec, [])
            if cm1 != cm2:
                diffs.setdefault('comments', {})[sec] = (cm1, cm2)
        return diffs
