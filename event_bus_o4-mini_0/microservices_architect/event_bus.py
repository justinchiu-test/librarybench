import threading
import time
import copy

def _matches(pattern, topic):
    """
    Match a topic against a pattern with RabbitMQ-style wildcards:
    '*' matches exactly one word, '#' matches zero or more words.
    Words are dot-separated.
    """
    p_parts = pattern.split('.')
    t_parts = topic.split('.')
    return _match_parts(p_parts, t_parts)

def _match_parts(p_parts, t_parts):
    i = j = 0
    while i < len(p_parts):
        part = p_parts[i]
        # '#' matches zero or more segments
        if part == '#':
            # if it's the last pattern part, it matches the rest
            if i == len(p_parts) - 1:
                return True
            # otherwise, try to match the remainder of the pattern
            # against all possible suffixes of the topic
            for k in range(j, len(t_parts) + 1):
                if _match_parts(p_parts[i+1:], t_parts[k:]):
                    return True
            return False
        # if we've run out of topic parts, no match
        if j >= len(t_parts):
            return False
        # '*' matches exactly one segment
        if part == '*':
            i += 1
            j += 1
            continue
        # literal match
        if part != t_parts[j]:
            return False
        i += 1
        j += 1
    # must have consumed all topic parts to match
    return j == len(t_parts)

class EventBus:
    def __init__(self):
        self.subscriptions = []  # list of (pattern, handler)
        self.dlq = []  # list of (topic, event)
        self.acked = set()
        self.error_hooks = {}  # scope -> list of callbacks
        self.retry_policies = {}  # topic -> policyOptions
        self.plugins = []  # list of plugin modules
        self.context = {}
        self.lock = threading.Lock()

    def scheduleDelivery(self, topic, event, delayMs):
        def _deliver():
            self.publishSync(topic, event)
        timer = threading.Timer(delayMs / 1000.0, _deliver)
        timer.daemon = True
        timer.start()

    def routeToDeadLetterQueue(self, topic, event):
        with self.lock:
            self.dlq.append((topic, event))

    def subscribeWithWildcard(self, pattern, handler):
        with self.lock:
            self.subscriptions.append((pattern, handler))

    def ackEvent(self, eventId):
        with self.lock:
            self.acked.add(eventId)

    def registerErrorHook(self, scope, callback):
        with self.lock:
            self.error_hooks.setdefault(scope, []).append(callback)

    def publishSync(self, topic, event):
        # propagate context
        if self.context:
            event = event if isinstance(event, dict) else {}
            event['context'] = copy.deepcopy(self.context)
        # plugin onPublish
        for plugin in self.plugins:
            if hasattr(plugin, 'onPublish'):
                try:
                    plugin.onPublish(topic, event)
                except Exception:
                    pass
        # dispatch to handlers
        for pattern, handler in list(self.subscriptions):
            if _matches(pattern, topic):
                # dispatch with retry support
                self._dispatch_with_retry(topic, event, handler)

    def publishBatch(self, events):
        for e in events:
            if isinstance(e, tuple) and len(e) == 2:
                topic, event = e
            elif isinstance(e, dict) and 'topic' in e and 'event' in e:
                topic, event = e['topic'], e['event']
            else:
                continue
            self.publishSync(topic, event)

    def propagateContext(self, ctx):
        with self.lock:
            self.context = ctx

    def setRetryPolicy(self, topic, policyOptions):
        with self.lock:
            self.retry_policies[topic] = policyOptions

    def registerPlugin(self, pluginModule):
        with self.lock:
            self.plugins.append(pluginModule)

    def _run_error_hooks(self, scope, error, topic, event):
        # global hooks
        for hook in self.error_hooks.get('global', []):
            try:
                hook('global', error, topic, event)
            except Exception:
                pass
        # specific scope hooks
        for hook in self.error_hooks.get(scope, []):
            try:
                hook(scope, error, topic, event)
            except Exception:
                pass

    def _dispatch_with_retry(self, topic, event, handler):
        attempts = event.get('_retry_attempts', 0)
        # check if there's an explicit retry policy for this topic
        has_policy = topic in self.retry_policies
        policy = self.retry_policies.get(topic, {}) if has_policy else {}
        max_retries = policy.get('retries', 0) if has_policy else 0

        # prepare backoff if needed
        backoff = None
        if has_policy:
            if policy.get('type') == 'fixed':
                delayMs = policy.get('delayMs', 0)
                backoff = lambda a, delayMs=delayMs: delayMs
            elif policy.get('type') == 'exponential':
                base = policy.get('initialDelayMs', 0)
                backoff = lambda a, base=base: base * (2 ** a)
            elif 'backoffFunction' in policy:
                backoff = policy['backoffFunction']

        try:
            handler(event)
        except Exception as e:
            # run error hooks
            self._run_error_hooks(topic, e, topic, event)
            if has_policy:
                # schedule up to max_retries times, then stop (no DLQ for policy)
                if attempts < max_retries:
                    next_attempts = attempts + 1
                    new_event = copy.deepcopy(event)
                    new_event['_retry_attempts'] = next_attempts
                    delay = backoff(attempts) if backoff else 0
                    self.scheduleDelivery(topic, new_event, delay)
            else:
                # no policy: dead-letter immediately
                self.routeToDeadLetterQueue(topic, event)
