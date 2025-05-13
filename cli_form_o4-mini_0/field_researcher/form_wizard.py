import json
import os
from datetime import datetime

class FormWizard:
    def __init__(self):
        # initialize questions: id, category: demographics 0-9, environment 10-29, feedback 30-49
        self.questions = []
        for i in range(50):
            if i < 10:
                category = 'Demographics'
            elif i < 30:
                category = 'Environment'
            else:
                category = 'Feedback'
            self.questions.append({'id': i, 'text': f'Question {i}', 'category': category, 'response': None})
        self.current_index = 0
        self.history = []
        self.forward_stack = []
        self.accessibility = {'high_contrast': False, 'screen_reader_cues': False}
        self.curses_initialized = False
        self.audit_log = []
        self.pages = []
        self._init_pages()
        self.plugins = {}

    def _init_pages(self):
        # pages: list of dict with name and question ids
        self.pages = [
            {'name': 'Demographics', 'questions': list(range(0,10))},
            {'name': 'Environment', 'questions': list(range(10,30))},
            {'name': 'Feedback', 'questions': list(range(30,50))}
        ]

    def real_time_validate(self, value, min=None, max=None):
        try:
            num = float(value)
        except (ValueError, TypeError):
            return False
        if min is not None and num < min:
            return False
        if max is not None and num > max:
            return False
        return True

    def apply_skip_logic(self, answer, question):
        # if question category environment and answer Indoors, skip all environment questions
        if question.get('category') == 'Environment' and answer == 'Indoors':
            skipped = [q['id'] for q in self.questions if q['category']=='Environment']
            return skipped
        return []

    def navigate_next(self):
        if self.current_index < len(self.questions) - 1:
            self.history.append(self.current_index)
            self.current_index += 1
            self.forward_stack.clear()
        return self.questions[self.current_index]

    def navigate_prev(self):
        if self.history:
            self.forward_stack.append(self.current_index)
            self.current_index = self.history.pop()
        return self.questions[self.current_index]

    def jump_to(self, index):
        if 0 <= index < len(self.questions):
            self.history.append(self.current_index)
            self.current_index = index
            self.forward_stack.clear()
        return self.questions[self.current_index]

    def enable_accessibility_mode(self):
        self.accessibility['high_contrast'] = True
        self.accessibility['screen_reader_cues'] = True

    def init_curses_renderer(self):
        # stub for curses
        self.curses_initialized = True
        return True

    def audit_log_event(self, event_type, details):
        timestamp = datetime.utcnow().isoformat()
        entry = {'timestamp': timestamp, 'event': event_type, 'details': details}
        self.audit_log.append(entry)

    def start_wizard(self):
        self._init_pages()
        self.current_index = 0
        self.history.clear()
        self.forward_stack.clear()

    def save_session(self, filepath):
        data = {
            'questions': self.questions,
            'current_index': self.current_index,
            'audit_log': self.audit_log
        }
        with open(filepath,'w') as f:
            json.dump(data, f)

    def load_session(self, filepath):
        if not os.path.exists(filepath):
            return False
        with open(filepath,'r') as f:
            data = json.load(f)
        self.questions = data.get('questions', self.questions)
        self.current_index = data.get('current_index',0)
        self.audit_log = data.get('audit_log', [])
        return True

    def register_plugin(self, name, handler):
        self.plugins[name] = handler

    def branch_flow(self, health_risk_answer):
        # reorder pages: if High then D->Feedback->Environment else default
        if health_risk_answer == 'High':
            dem = next(p for p in self.pages if p['name']=='Demographics')
            env = next(p for p in self.pages if p['name']=='Environment')
            fb = next(p for p in self.pages if p['name']=='Feedback')
            self.pages = [dem, fb, env]
        else:
            self._init_pages()
        return self.pages
