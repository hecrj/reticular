# coding=utf-8
"""
Reticular is a lightweight Python module that can be used to create powerful command-line tools.
It lets you define commands easily, without losing flexibility and control.
It can handle subcommand groups and supports interactive mode!
"""
import importlib

__author__ = "Héctor Ramón Jiménez, and Alvaro Espuña Buxo"

from functools import wraps
import os
import sys
from argparse import ArgumentParser

_COMMAND_GROUPS = {}

try:
    input = raw_input
except:
    pass

class CLI(object):
    def __init__(self, name, version, message='Welcome!', package='commands'):
        self.name = name
        self.message = message
        self.groups = {}
        self.interactive_mode = False

        for path in self.list(name, package):
            if path not in _COMMAND_GROUPS:
                _COMMAND_GROUPS[path] = CommandGroup(path)

            group = _COMMAND_GROUPS[path]
            self.groups[group.name] = group

        try:
            self.base = self.groups.pop('base')
            self.base.load(subcommand=False)
            self.base.populate()
            self.base.parser.add_argument('--version', action='version', version=version)
        except KeyError:
            raise RuntimeError('Base commands module not found in: %s.base' % package)

        self.load_all()

    def run(self, args=sys.argv[1:]):
        if len(args) < 1:
            if self.interactive_mode:
                return
            else:
                return self.interactive()

        try:
            parsed_args = self.base.parser.parse_args(args)
            parsed_args = vars(parsed_args)
            func = parsed_args.pop('func', None)
            if func is None:
                try:
                    self.groups[args[0]].parser.error("invalid number of arguments")
                except KeyError:
                    self.base.parser.error("invalid base command")
            else:
                func(**parsed_args)
        except RuntimeError as e:
            print('ERROR: ' + str(e))

    def interactive(self):
        self.interactive_mode = True
        print(self.message)

        while True:
            try:
                args = input('>> ').split()
                self.run(args)
            except EOFError:
                print()
                exit(0)
            except KeyboardInterrupt:
                print()
                exit(1)
            except SystemExit:
                pass

    def load_all(self):
        for name, cmd_group in self.groups.items():
            cmd_group.load()
            cmd_group.populate()
            cmd_group.register(self.base.parser_generator)

    @staticmethod
    def list(name, package):
        module = "%s.%s" % (name, package)

        try:
            commands = importlib.import_module(module)
            pathname = os.path.dirname(commands.__file__)
            return ("%s.%s.%s" % (name, package, os.path.splitext(f)[0])
                    for f in os.listdir(pathname) if f.endswith('.py') and not f.startswith('_'))
        except ImportError:
            raise RuntimeError("%s package not found" % module)


class CommandGroup(object):
    def __init__(self, path):
        self.name = path.split('.')[-1]
        self.path = path
        self._module = None
        self.parser = None
        self.parser_generator = None
        self.parsers = {}

    def load(self, subcommand=True):
        if not self.parser:
            add_help = False if subcommand else True
            prog = ' '+self.name if subcommand else ''
            title = 'commands' if subcommand else 'base commands'
            metavar = '<command>' if subcommand else '<base_command>'
            self.parser = DefaultHelpParser(add_help=add_help, prog=sys.argv[0]+prog)
            self.parser_generator = self.parser.add_subparsers(title=title, metavar=metavar)
            self._module = __import__(self.path, fromlist=[self.name])

    def register(self, subparsers):
        subparsers.add_parser(self.name, parents=[self.parser], help=self.parser.description,
                              description=self.parser.description)

    def populate(self):
        self.parser.description = self._module.__doc__

        for cmd, parser in self.parsers.items():
            for args, kwargs in getattr(self._module, 'ARGUMENTS', []):
                parser.add_argument(*args, **kwargs)


class DefaultHelpParser(ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def argument(*args, **kwargs):
    def decorator(f):
        try:
            _get_parser(f).add_argument(*args, **kwargs)
        except KeyError:
            pass

        return f
    return decorator


def command(f):
    try:
        _get_parser(f)
    except KeyError:
        pass

    return f


def global_arg(*args, **kwargs):
    return args, kwargs


class say:
    INDENTATION = 0

    def __init__(self, *args):
        for s in args:
            print(('  ' * say.INDENTATION) + s)

    def __enter__(self):
        say.INDENTATION += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        say.INDENTATION -= 1


def _get_parser(f):
    """
    Gets the parser for the command f, if it not exists it creates a new one
    """
    _COMMAND_GROUPS[f.__module__].load()

    if f.__name__ not in _COMMAND_GROUPS[f.__module__].parsers:
        parser = _COMMAND_GROUPS[f.__module__].parser_generator.add_parser(f.__name__, help=f.__doc__,
                                                                           description=f.__doc__)
        parser.set_defaults(func=f)

        _COMMAND_GROUPS[f.__module__].parsers[f.__name__] = parser

    return _COMMAND_GROUPS[f.__module__].parsers[f.__name__]


def superuser(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if os.getuid() != 0:
            raise RuntimeError('To perform this command you need super user privileges.')

        return f(*args, **kwargs)
    return wrapper
