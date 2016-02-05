import yaml

from abc import abstractmethod

from jinja2 import Template, Environment, FileSystemLoader

from sonny.infrastructure.context import helpers

from sonny.infrastructure.operations.base import BaseOperation


class BaseTemplater(BaseOperation):
    @abstractmethod
    def render(self, template_context):
        pass


# Perhaps we do need to see the output in test
# @BaseTemplater.auto_mock_for_local_testing
class Jinja2Templater(BaseTemplater):
    filters_registry = {}

    @classmethod
    def register_named_filter(cls, name):
        def do_register_named_filter(func):
            cls.filters_registry[name] = func

            return func

        return do_register_named_filter

    @classmethod
    def register_filter(cls, func):
        return cls.register_named_filter(func.func_name)(func)

    def __init__(self, template_name, template_path=None):
        if template_path:
            self.environment = Environment(loader=FileSystemLoader(template_path))
            self.environment.filters.update(self.filters_registry)
            self.template = self.environment.get_template(template_name)
        else:
            self.environment = None
            with open(template_name, 'rb') as f:
                self.template = Template(f.read())

    @helpers.step
    def render(self, template_context):
        return self.template.render(**template_context)


@Jinja2Templater.register_filter
def yaml_dumps(value, **kwargs):
    return yaml.dump(value, **kwargs)


@BaseTemplater.register_default_noop
class PrintTemplater(BaseTemplater):
    def __init__(self, *args, **kwargs):
        pass

    @helpers.step
    def render(self, template_context):
        print 'Rendering template:'
        print template_context[:320]
