from functools import wraps

import utils


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


def function_using_current_frame(*frargs):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            frame = context.current_frame
            if frargs:
                frame_args = tuple(getattr(frame, frarg) for frarg in frargs)
            else:
                frame_args = (frame,)
            injected_args = frame_args + args
            return func(*injected_args, **kwargs)

        return decorated

    if utils.is_argumentless_decorator(frargs):
        func = frargs[0]
        frargs = tuple()
        return decorator(func)
    else:
        return decorator


def method_using_current_frame(*frargs):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            frame = context.current_frame
            if frargs:
                frame_args = tuple(getattr(frame, frarg) for frarg in frargs)
            else:
                frame_args = (frame,)
            injected_args = args[:1] + frame_args + args[1:]
            return func(*injected_args, **kwargs)

        return decorated

    if utils.is_argumentless_decorator(frargs):
        func = frargs[0]
        frargs = tuple()
        return decorator(func)
    else:
        return decorator
