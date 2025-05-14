import requests

class GitLabCIPlugin:
    def __init__(self, project_id, token):
        self.project_id = project_id
        self.token = token
        self.endpoint = f'https://gitlab.com/api/v4/projects/{self.project_id}/trigger/pipeline'

    def on_event(self, path, event):
        data = {
            'token': self.token,
            'ref': 'master',
            'variables[FILE]': path,
            'variables[EVENT]': event
        }
        try:
            requests.post(self.endpoint, data=data)
        except Exception:
            pass
