import asyncio
from conexia.core import AsyncSTUNClient


async def main():
    client = AsyncSTUNClient(cache_backend="file")
    stun_info = await client.get_stun_info()
    #user_id = await client.get_user_id()
    #public_ip = await client.get_public_ip()
    #public_port = await client.get_public_port()
    #nat_type = await client.get_nat_type()

    # Print CLI output
    print("STUN Result:", stun_info)


def cli_entry_point():
    """ Entry point for the CLI command `conexia` """
    # This function serves as a syncronous wrapper for 
    # the async main function
    asyncio.run(main())  # ✅ Ensures async execution


if __name__ == "__main__":
    cli_entry_point()

# Run using: python -m conexia.cli