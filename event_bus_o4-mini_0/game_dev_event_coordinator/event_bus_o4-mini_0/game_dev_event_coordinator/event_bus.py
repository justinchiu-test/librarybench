import threading
import time

class EventBus:
    def __init__(self):
        self.reset()

    def reset(self):
        self.subscribers = []  # list of (pattern, handler)
        self.dead_letter_queue = []  # list of (topic, event)
        self.acked_events = set()
        self.error_hooks = {}  # scope -> list of callbacks
        self.retry_policies = {}  # topic -> policyOptions
        self.current_context = None
        self.plugins = []

    def subscribeWithWildcard(self, pattern, handler):
        self.subscribers.append((pattern, handler))

    def routeToDeadLetterQueue(self, topic, event):
        self.dead_letter_queue.append((topic, event))

    def ackEvent(self, eventId):
        self.acked_events.add(eventId)

    def registerErrorHook(self, scope, callback):
        self.error_hooks.setdefault(scope, []).append(callback)

    def publishSync(self, topic, event):
        for pattern, handler in list(self.subscribers):
            if self._match_pattern(pattern, topic):
                policy = self.retry_policies.get(topic)
                attempts = policy.get('retries', 0) + 1 if policy else 1
                for attempt in range(1, attempts + 1):
                    try:
                        handler(topic, event, self.current_context)
                        break
                    except Exception as e:
                        # pattern‐specific hooks
                        for hook in self.error_hooks.get(pattern, []):
                            hook(e, topic, event)
                        # global hooks
                        for hook in self.error_hooks.get('global', []):
                            hook(e, topic, event)
                        if attempt == attempts:
                            # final failure
                            self.routeToDeadLetterQueue(topic, event)
                        else:
                            # retry delay if specified
                            if policy and policy.get('delayMs', 0) > 0:
                                time.sleep(policy['delayMs'] / 1000.0)

    def publishBatch(self, events):
        for item in events:
            topic = item.get('topic')
            event = item.get('event')
            self.publishSync(topic, event)

    def propagateContext(self, ctx):
        self.current_context = ctx

    def setRetryPolicy(self, topic, policyOptions):
        self.retry_policies[topic] = policyOptions

    def registerPlugin(self, pluginModule):
        self.plugins.append(pluginModule)
        if hasattr(pluginModule, 'init'):
            pluginModule.init(self)

    def scheduleDelivery(self, topic, event, delayMs):
        def deliver():
            self.publishSync(topic, event)
        timer = threading.Timer(delayMs / 1000.0, deliver)
        timer.daemon = True
        timer.start()
        return timer

    def _match_pattern(self, pattern, topic):
        p_tokens = pattern.split('.')
        t_tokens = topic.split('.')
        return self._match_tokens(p_tokens, t_tokens)

    def _match_tokens(self, p_tokens, t_tokens):
        def match(p_i, t_i):
            while p_i < len(p_tokens) and t_i < len(t_tokens):
                p_tok = p_tokens[p_i]
                if p_tok == '#':
                    # match zero or more
                    if p_i + 1 == len(p_tokens):
                        return True
                    for skip in range(t_i, len(t_tokens) + 1):
                        if match(p_i + 1, skip):
                            return True
                    return False
                if p_tok == '*':
                    # match exactly one
                    p_i += 1
                    t_i += 1
                    continue
                if p_tok != t_tokens[t_i]:
                    return False
                p_i += 1
                t_i += 1
            # allow trailing '#' to consume empties
            while p_i < len(p_tokens) and p_tokens[p_i] == '#':
                p_i += 1
            return p_i == len(p_tokens) and t_i == len(t_tokens)
        return match(0, 0)

# the singleton / module‐level API
default_bus = EventBus()

def resetBus():
    default_bus.reset()

def subscribeWithWildcard(pattern, handler):
    default_bus.subscribeWithWildcard(pattern, handler)

def routeToDeadLetterQueue(topic, event):
    default_bus.routeToDeadLetterQueue(topic, event)

def ackEvent(eventId):
    default_bus.ackEvent(eventId)

def registerErrorHook(scope, callback):
    default_bus.registerErrorHook(scope, callback)

def publishSync(topic, event):
    default_bus.publishSync(topic, event)

def publishBatch(events):
    default_bus.publishBatch(events)

def propagateContext(ctx):
    default_bus.propagateContext(ctx)

def setRetryPolicy(topic, policyOptions):
    default_bus.setRetryPolicy(topic, policyOptions)

def registerPlugin(pluginModule):
    default_bus.registerPlugin(pluginModule)

def scheduleDelivery(topic, event, delayMs):
    return default_bus.scheduleDelivery(topic, event, delayMs)
