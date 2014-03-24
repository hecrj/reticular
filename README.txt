reticular
===============
reticular is a lightweight Python module that can be used to create powerful command-line tools.
It lets you define commands easily, without losing flexibility and control.
It can handle subcommand groups and supports interactive mode!

Installation
-----------------
```shell
$ pip install reticular
```

Usage
-----------------
First, you need to create the script to run your command-line tool. Let's call it `run`:

```python
#!/usr/bin/env python

import reticular

reticular.CLI(
    name='example',     # Name of the tool
    version='0.0.1',    # Version of the tool
    message="Welcome!"  # Welcome message shown when entering interactive mode
).run()
```

By default, `reticular` in the example above will try to load the modules located in `example.commands` as groups of
commands. The module `example.commands.base` must exist, the commands defined in this module are base commands and they
don't belong to a particular command group. Therefore, if we want `reticular` to be able to find our commands the
structure of the project should look like this:

```
cli-app
|--example
|  |--commands
|  |  |--__init__.py
|  |  |--base.py
|  |  |--...
|  |--__init__.py
|  |--...
|--run
```

Suppose that we want to have a base command `hello` that says `Hello World!`. That's easy, we write in
`example.commands.base`:

```python
"""
An example of how to use reticular!
"""
from reticular import command

@command # Command without arguments
def hello():
    """
    Says hello!
    """
    print("Hello World!")

```

Now, we are able to do:
```shell
$ ./run hello
Hello World!
```

Nice! But we can do the same interactively! Look:

```shell
$./run 
Welcome!
>> --help
usage: ./run [-h] [--version] <base_command> ...

An example of how to use reticular!

optional arguments:
  -h, --help      show this help message and exit
  --version       show program's version number and exit

base commands:
  <base_command>
    hello         Says hello!
>> hello
Hello World!
```

As you can see the help is automatically generated for every base command and group of commands.

Now, let's try to create a command in a command group that adds two integers. `math` seems like a good name for the
command group, and the command itself can be called `add`. Let's do this! We just need to create the module
`example.commands.math` like this:

```python
"""
Math commands
"""
from reticular import argument

@argument("b", help="An integer", type=int)
@argument("a", help="An integer", type=int)
def add(a, b):
    """
    Adds two integers
    """
    print("%d" % (a+b))
```

And now...
```shell
./run math add 41 32
73
```

Cool! The `@argument` decorator can take the same `args` and `kwargs` than the `add_argument` method of the
`argparse`'s module. That's because reticular uses `argparse` internally!
