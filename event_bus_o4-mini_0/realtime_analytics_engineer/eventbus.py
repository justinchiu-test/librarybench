import threading
import time
import re
import random

class EventBus:
    def __init__(self):
        self.subscriptions = []  # list of (regex, pattern, handler)
        self.dead_letter_queue = []
        self.error_hooks = {'global': [], 'topic': {}}
        self.retry_policies = {}  # topic -> policyOptions
        self.acked = set()
        self.context = {}
        self.plugins = []
        self.lock = threading.Lock()

    def subscribeWithWildcard(self, pattern, handler):
        regex = self._pattern_to_regex(pattern)
        compiled = re.compile('^' + regex + '$')
        self.subscriptions.append((compiled, pattern, handler))

    def _pattern_to_regex(self, pattern):
        res = []
        i = 0
        while i < len(pattern):
            c = pattern[i]
            if c == '.':
                res.append(r'\.')
                i += 1
            elif c == '*':
                res.append(r'[^\.]+')
                i += 1
            elif c == '{':
                j = pattern.find('}', i)
                opts = pattern[i+1:j].split(',')
                escaped = [re.escape(o) for o in opts]
                res.append('(' + '|'.join(escaped) + ')')
                i = j + 1
            else:
                res.append(re.escape(c))
                i += 1
        return ''.join(res)

    def publishSync(self, topic, event, ctx=None):
        ctx = ctx or {}
        eventId = id(event)
        self.propagateContext(ctx)
        self._deliver_event(topic, event, eventId, attempt=0)
        return eventId

    def publishBatch(self, events):
        for topic, event in events:
            self.publishSync(topic, event)

    def scheduleDelivery(self, topic, event, delayMs):
        timer = threading.Timer(delayMs / 1000.0, lambda: self.publishSync(topic, event))
        timer.daemon = True
        timer.start()

    def routeToDeadLetterQueue(self, topic, event):
        with self.lock:
            self.dead_letter_queue.append((topic, event))

    def ackEvent(self, eventId):
        with self.lock:
            self.acked.add(eventId)

    def registerErrorHook(self, scope, callback):
        if scope == 'global':
            self.error_hooks['global'].append(callback)
        else:
            self.error_hooks['topic'].setdefault(scope, []).append(callback)

    def propagateContext(self, ctx):
        self.context = ctx.copy()

    def setRetryPolicy(self, topic, policyOptions):
        self.retry_policies[topic] = policyOptions

    def registerPlugin(self, pluginModule):
        if hasattr(pluginModule, 'register'):
            pluginModule.register(self)
        self.plugins.append(pluginModule)

    def _call_error_hooks(self, topic, event, exception):
        for cb in self.error_hooks['global']:
            try:
                cb(topic, event, exception)
            except Exception:
                pass
        for cb in self.error_hooks['topic'].get(topic, []):
            try:
                cb(topic, event, exception)
            except Exception:
                pass

    def _deliver_event(self, topic, event, eventId, attempt):
        # if the event has been acknowledged, do not proceed
        with self.lock:
            if eventId in self.acked:
                return

        # find matching handlers
        for regex, pat_str, handler in self.subscriptions:
            if regex.match(topic):
                try:
                    handler(event, self.context)
                except Exception as e:
                    self._call_error_hooks(topic, event, e)
                    policy = self.retry_policies.get(topic)
                    if policy:
                        max_attempts = policy.get('maxRetries', 0)
                        if attempt < max_attempts:
                            # check ack again before scheduling
                            with self.lock:
                                if eventId in self.acked:
                                    return
                            initial = policy.get('initialDelay', 0)
                            bt = policy.get('backoffType', 'fixed')
                            if bt == 'exponential':
                                delay = initial * (2 ** attempt)
                            elif bt == 'jitter':
                                lo, hi = policy.get('jitterRange', (0, initial))
                                delay = random.uniform(lo, hi)
                            else:  # fixed
                                delay = initial
                            timer = threading.Timer(delay / 1000.0,
                                                     lambda: self._deliver_event(topic, event, eventId, attempt + 1))
                            timer.daemon = True
                            timer.start()
                        else:
                            self.routeToDeadLetterQueue(topic, event)
                    else:
                        self.routeToDeadLetterQueue(topic, event)
