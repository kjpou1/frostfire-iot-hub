# app/models/__init__.py
from .singleton import SingletonMeta
from .command_line_args import CommandLineArgs

__all__ = ['SingletonMeta', 'CommandLineArgs']
