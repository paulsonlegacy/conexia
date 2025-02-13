import asyncio
from conexia.core import STUNClient


async def main():
    client = STUNClient(cache_backend="file")  # Change to "memory", "file", "sqlite", "redis" as needed
    user_id = await client.get_user_id()
    public_ip = await client.get_public_ip()
    public_port = await client.get_public_port()
    nat_type = await client.get_nat_type()

    print("User ID:", user_id)
    print("Public IP:", public_ip)
    print("Public Port:", public_port)
    print("NAT Type:", nat_type)

# conexia.cli:cli_entry_point makes sure asyncio.run(main()) is properly executed.
# The cli_entry_point() wrapper ensures that the CLI script runs as expected.
def cli_entry_point():
    """ Entry point for the CLI command `conexia` """
    asyncio.run(main())  # ✅ Ensures async execution


if __name__ == "__main__":
    cli_entry_point()

# Run using: python -m conexia.cli