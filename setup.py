# coding=utf-8
# reticular setup.py
from distutils.core import setup

setup(
    name="reticular",
    py_modules=["reticular"],
    version="0.0.1",
    description="Lightweight module to create powerful command-line tools",
    author="Héctor Ramón Jiménez",
    author_email="hector0193@gmail.com",
    url="https://github.com/hacs/reticular",
    keywords=["command", "line", "tool"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description="""\
reticular is a lightweight Python module that can be used to create powerful command-line tools.
It lets you define commands easily, without losing flexibility and control.
It can handle subcommand groups and supports interactive mode!
"""
)
