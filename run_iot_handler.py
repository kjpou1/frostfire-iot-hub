import asyncio
import logging

from app.iot_handler.iot_handler import IotHandler
from app.runtime.command_line import CommandLine

logger = logging.getLogger(__name__)


async def main_async(): 

    try:
        args = CommandLine.parse_arguments()
        # Create an instance of IotHandler
        instance = IotHandler(args)
        # Run the async main function with the parsed arguments
        await instance.run_async()
        pass
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
