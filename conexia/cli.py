import asyncio
from conexia.core import AsyncSTUNClient


async def main() -> str:
    client = AsyncSTUNClient(cache_backend="file")
    network_info = await client.get_network_info()

    # Print CLI output
    print("STUN Result:", network_info)


def cli_entry_point():
    """ Entry point for the CLI command `conexia` """
    # This function serves as a syncronous wrapper for 
    # the async main function
    asyncio.run(main())  # ✅ Ensures async execution


if __name__ == "__main__":
    cli_entry_point()

# Run using: python -m conexia.cli