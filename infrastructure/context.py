from functools import wraps


class ContextContextManager(object):
    def __init__(self, context, frame):
        self.context = context
        self.frame = frame

    def __enter__(self):
        self.context._push(self.frame)

        return self.frame

    def __exit__(self, _type, value, traceback):
        popped = self.context._pop()
        assert popped == self.frame, "Popped frame was not the same as pushed"


class Frame(object):
    pass


class Context(object):
    def __init__(self):
        self.frames = []

    def new_frame(self, frame=None):
        if frame is None:
            frame = Frame()
        return ContextContextManager(self, frame)

    def _push(self, frame):
        self.frames.append(frame)

    def _pop(self):
        return self.frames.pop()

    @property
    def current_frame(self):
        return self.frames[-1]


# Global context
context = Context()


def function_using_current_frame(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        frame = context.current_frame
        injected_args = (frame,) + args
        return func(*injected_args, **kwargs)

    return decorated


def method_using_current_frame(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        frame = context.current_frame
        injected_args = args[:1] + (frame,) + args[1:]
        return func(*injected_args, **kwargs)

    return decorated
