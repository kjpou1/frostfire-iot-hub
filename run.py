import asyncio
import logging

from app import CommandLine
from app.host import Host

logger = logging.getLogger(__name__)


async def main_async():

    try:
        args = CommandLine.parse_arguments()
        # Create an instance of Host with parsed arguments
        instance = Host(args)
        # Run the async main function with the parsed arguments
        await instance.run_async()
    except ValueError as e:
        logger.error("Error: %s", e)


def main():
    asyncio.run(main_async())


if __name__ == '__main__':
    # Setup logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    main()
