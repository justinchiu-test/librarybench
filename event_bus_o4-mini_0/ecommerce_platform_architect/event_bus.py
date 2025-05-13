import time

class EventBus:
    def __init__(self):
        self.subscriptions = []  # list of tuples (pattern, handler)
        self.scheduled = []  # list of tuples (due_ms, topic, event)
        self.dead_letter_queue = []  # list of tuples (topic, event)
        self.in_flight = set()  # set of eventIds
        self.error_hooks = {'global': []}  # scope -> list of callbacks
        self.retry_policy = {}  # topic -> options dict
        self.plugins = []  # list of plugin modules
        self.context = None

    def scheduleDelivery(self, topic, event, delayMs):
        due = int(time.time() * 1000) + delayMs
        self.scheduled.append((due, topic, event))

    def routeToDeadLetterQueue(self, topic, event):
        self.dead_letter_queue.append((topic, event))

    def subscribeWithWildcard(self, pattern, handler):
        self.subscriptions.append((pattern, handler))

    def ackEvent(self, eventId):
        self.in_flight.discard(eventId)

    def registerErrorHook(self, scope, callback):
        if scope not in self.error_hooks:
            self.error_hooks[scope] = []
        self.error_hooks[scope].append(callback)

    def publishSync(self, topic, event):
        self._add_context(event)
        self._apply_plugins('pre_publish', topic, event)
        event_id = event.get('id')
        if event_id:
            self.in_flight.add(event_id)
        try:
            self._dispatch(topic, event)
        except Exception as e:
            self._handle_error_hooks(topic, event, e)
        self._apply_plugins('post_publish', topic, event)

    def publishBatch(self, events):
        for topic, event in events:
            self.publishSync(topic, event)

    def propagateContext(self, ctx):
        self.context = ctx

    def setRetryPolicy(self, topic, policyOptions):
        self.retry_policy[topic] = policyOptions

    def registerPlugin(self, pluginModule):
        self.plugins.append(pluginModule)

    def publish(self, topic, event):
        """
        Publish with retry/backoff and DLQ routing
        """
        self._add_context(event)
        self._apply_plugins('pre_publish', topic, event)
        event_id = event.get('id')
        if event_id:
            self.in_flight.add(event_id)
        max_retries = self.retry_policy.get(topic, {}).get('max_retries', 0)
        attempt = 0
        while True:
            try:
                self._dispatch(topic, event)
                break
            except Exception as e:
                attempt += 1
                self._handle_error_hooks(topic, event, e)
                if attempt > max_retries:
                    self.routeToDeadLetterQueue(topic, event)
                    break
        self._apply_plugins('post_publish', topic, event)

    # Internal helpers

    def _add_context(self, event):
        if self.context is not None:
            event.setdefault('ctx', {}).update(self.context)

    def _apply_plugins(self, hook, topic, event):
        for plugin in self.plugins:
            fn = getattr(plugin, hook, None)
            if callable(fn):
                try:
                    fn(topic, event)
                except Exception:
                    pass

    def _handle_error_hooks(self, topic, event, error):
        # global hooks
        for cb in self.error_hooks.get('global', []):
            try:
                cb(topic, event, error)
            except Exception:
                pass
        # topic-specific
        for cb in self.error_hooks.get(topic, []):
            try:
                cb(topic, event, error)
            except Exception:
                pass

    def _dispatch(self, topic, event):
        matched = False
        for pattern, handler in self.subscriptions:
            if self._match(topic, pattern):
                matched = True
                handler(event)
        if not matched:
            # no subscribers: no-op
            pass

    def _match(self, topic, pattern):
        t_segs = topic.split('.')
        p_raw = pattern.split('.')
        p_segs = []
        for seg in p_raw:
            if seg.startswith('{') and seg.endswith('}'):
                opts = seg[1:-1].split(',')
                p_segs.append(opts)
            else:
                p_segs.append(seg)

        def rec(ti, pi):
            if pi == len(p_segs):
                return ti == len(t_segs)
            pat = p_segs[pi]
            if pat == '#':
                # match zero or more
                if pi + 1 == len(p_segs):
                    return True
                for skip in range(ti, len(t_segs) + 1):
                    if rec(skip, pi + 1):
                        return True
                return False
            if ti >= len(t_segs):
                return False
            if pat == '*':
                return rec(ti + 1, pi + 1)
            if isinstance(pat, list):
                if t_segs[ti] in pat:
                    return rec(ti + 1, pi + 1)
                return False
            if pat == t_segs[ti]:
                return rec(ti + 1, pi + 1)
            return False

        return rec(0, 0)
