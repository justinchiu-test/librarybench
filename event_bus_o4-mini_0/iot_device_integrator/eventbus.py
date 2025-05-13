import time

class EventBus:
    def __init__(self):
        self.subscriptions = []  # list of (pattern, handler)
        self.dead_letter_queue = []  # list of dicts with topic and event
        self.scheduled_tasks = []  # list of dicts with exec_time, topic, event
        self.retry_policies = {}  # topic -> policyOptions
        self.error_hooks = []  # list of (scope, callback)
        self.acked_events = set()
        self.context = {}

    def propagateContext(self, ctx):
        self.context = ctx

    def subscribeWithWildcard(self, pattern, handler):
        self.subscriptions.append((pattern, handler))

    def registerErrorHook(self, scope, callback):
        self.error_hooks.append((scope, callback))

    def routeToDeadLetterQueue(self, topic, event):
        e = self._prepare_event(event)
        self.dead_letter_queue.append({'topic': topic, 'event': e})

    def scheduleDelivery(self, topic, event, delayMs):
        now_ms = int(time.time() * 1000)
        exec_time = now_ms + delayMs
        self.scheduled_tasks.append({'exec_time': exec_time, 'topic': topic, 'event': event})

    def processScheduled(self):
        now_ms = int(time.time() * 1000)
        due = [t for t in self.scheduled_tasks if t['exec_time'] <= now_ms]
        for t in due:
            self.publishSync(t['topic'], t['event'])
            self.scheduled_tasks.remove(t)

    def ackEvent(self, eventId):
        self.acked_events.add(eventId)

    def setRetryPolicy(self, topic, policyOptions):
        self.retry_policies[topic] = policyOptions

    def registerPlugin(self, pluginModule):
        if hasattr(pluginModule, 'setup') and callable(pluginModule.setup):
            pluginModule.setup(self)

    def publishSync(self, topic, event):
        e = self._prepare_event(event)
        for pattern, handler in self.subscriptions:
            if self.match_topic(topic, pattern):
                try:
                    handler(topic, e)
                except Exception as ex:
                    self._handle_error(topic, ex)

    def publishBatch(self, events):
        for item in events:
            topic = item.get('topic')
            event = item.get('event')
            self.publishSync(topic, event)

    def _prepare_event(self, event):
        if isinstance(event, dict):
            e = event.copy()
            e['ctx'] = self.context
            return e
        return {'event': event, 'ctx': self.context}

    def _handle_error(self, topic, exception):
        for scope, callback in self.error_hooks:
            if scope == 'global' or scope == topic:
                try:
                    callback(exception, self.context)
                except:
                    pass

    @staticmethod
    def match_topic(topic, pattern):
        t_parts = topic.split('.')
        p_parts = pattern.split('.')
        i = j = 0
        while i < len(t_parts) and j < len(p_parts):
            if p_parts[j] == '#':
                return True
            elif p_parts[j] == '*':
                i += 1
                j += 1
            elif p_parts[j] == t_parts[i]:
                i += 1
                j += 1
            else:
                return False
        if j < len(p_parts) and p_parts[j] == '#':
            return True
        return i == len(t_parts) and j == len(p_parts)
