import asyncio
from mcp import Client
async def main():
    async with Client("http://127.0.0.1:5000/mcp") as client:
    # Discover the available tools
        tools = await client.list_tools()
        print("Available MCP tools:")
        for tool in tools.tools:
            print("-", tool.name, tool.description, tool.input_schema) # Invoke the MongoDB tool
        result = await client.call_tool( "get_top_destinations", {"limit": 5} )
        print("\nMongoDB results:")
        print(result.content)
            # # Invoke the Redis tool
            # result = await client.call_tool( "get_statistics", {"key": "active_users"} )
            # print("\nRedis results:")
            # print(result.content)

asyncio.run(main())