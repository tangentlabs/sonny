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
