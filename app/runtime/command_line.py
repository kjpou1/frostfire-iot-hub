import argparse

from app.models import CommandLineArgs


class CommandLine:
    @staticmethod
    def parse_arguments() -> CommandLineArgs:
        parser = argparse.ArgumentParser(
            description='Run the application with specified arguments.')

        args = parser.parse_args()

        return CommandLineArgs()
