import utils
import logging


class Pipeline(object):
    @classmethod
    def with_no_input(cls, func):
        return WithNoInputOperation(func)

    @classmethod
    def taking_input(cls, func):
        return PipeOperation(None, WithInputOperation(func))

    @classmethod
    def map(cls, operation):
        return MapOperation(None, operation)


class BaseOperation(object):
    def pipe(self, func):
        return PipeOperation(self, WithInputOperation(func))

    def ignoring_input(self, func):
        return PipeOperation(self, WithNoInputOperation(func))

    def map(self, operation):
        return MapOperation(self, operation)

    def tee(self, *operations):
        return FanOutOperation(self, *operations)

    @utils.not_implemented
    def with_no_input(self):
        pass

    @utils.not_implemented
    def taking_input(self, value):
        pass

    def go(self):
        return self.with_no_input()


class WithNoInputOperation(BaseOperation):
    def __init__(self, func):
        self.func = func

    def with_no_input(self):
        return self.func()

    def taking_input(self, value):
        return self.with_no_input()

    def __str__(self):
        func_str = str(self.func)
        func_str = '\n'.join('*%s' % line for line in func_str.split('\n'))
        return '%s\nfunc:%s\n' % (self.__class__.__name__, func_str)


class WithInputOperation(BaseOperation):
    def __init__(self, func):
        self.func = func

    def taking_input(self, value):
        return self.func(value)

    def __str__(self):
        func_str = str(self.func)
        func_str = '\n'.join('*%s' % line for line in func_str.split('\n'))
        return '%s\nfunc:%s\n' % (self.__class__.__name__, func_str)


class PipeOperation(BaseOperation):
    def __init__(self, start_operation, *operations):
        self.start_operation = start_operation
        self.operations = operations
        self._merge_pipe_operations()

    def _merge_pipe_operations(self):
        if not isinstance(self.start_operation, PipeOperation):
            return

        start_operation = self.start_operation
        self.start_operation = start_operation.start_operation
        self.operations = start_operation.operations + self.operations

    def with_no_input(self):
        value = self.start_operation.with_no_input()
        return self.taking_input(value)

    def taking_input(self, value):
        for operation in self.operations:
            value = operation.taking_input(value)

        return value

    def __str__(self):
        start_operation_str = str(self.start_operation)
        start_operation_str = '\n'.join('*%s' % line for line in start_operation_str.split('\n'))
        operations_str = [str(operation) for operation in self.operations]
        operations_str = '\n'.join('\n'.join('*%s' % line for line in operation_str.split('\n')) for operation_str in operations_str)
        return '%s\nstart_operation:\n%s\noperations:\n%s\n' % (self.__class__.__name__, start_operation_str, operations_str)


class MapOperation(BaseOperation):
    def __init__(self, operation, mapped_operation):
        self.operation = operation
        self.mapped_operation = mapped_operation

    def with_no_input(self):
        values = self.operation.with_no_input()
        return self.taking_input(values)

    def taking_input(self, values):
        values = [
            self.mapped_operation.taking_input(value)
            for value in values
        ]

        return values

    def __str__(self):
        operation_str = str(self.operation)
        operation_str = '\n'.join('*%s' % line for line in operation_str.split('\n'))
        mapped_operation_str = str(self.mapped_operation)
        mapped_operation_str = '\n'.join('*%s' % line for line in mapped_operation_str.split('\n'))
        return '%s\noperation:\n%s\nmapped_operation:\n%s\n' % (self.__class__.__name__, operation_str, mapped_operation_str)


class FanOutOperation(BaseOperation):
    def __init__(self, start_operation, *operations):
        self.start_operation = start_operation
        self.operations = operations
        self._merge_fanout_operations()

    def _merge_fanout_operations(self):
        if not isinstance(self.start_operation, FanOutOperation):
            return

        start_operation = self.start_operation
        self.start_operation = start_operation.start_operation
        self.operations = start_operation.operations + self.operations

    def with_no_input(self):
        values = self.start_operation.with_no_input()
        return self.taking_input(values)

    def taking_input(self, values):
        values = [
            operation.taking_input(values)
            for operation in self.operations
        ]

        return values[0]

    def __str__(self):
        start_operation_str = str(self.start_operation)
        start_operation_str = '\n'.join('*%s' % line for line in start_operation_str.split('\n'))
        operations_str = [str(operation) for operation in self.operations]
        operations_str = '\n'.join('\n'.join('*%s' % line for line in operation_str.split('\n')) for operation_str in operations_str)
        return '%s\nstart_operation:\n%s\noperations:\n%s\n' % (self.__class__.__name__, start_operation_str, operations_str)
