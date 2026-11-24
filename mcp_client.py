import asyncio

from mcp import Client
from ollama import AsyncClient

MODEL = "qwen3.5:4b"


def mcp_tool_to_ollama(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.input_schema
        }
    }


async def main():

    ollama = AsyncClient()

    async with Client("http://127.0.0.1:5000/mcp") as client:

        tools = await client.list_tools()

        ollama_tools = [
            mcp_tool_to_ollama(tool)
            for tool in tools.tools
        ]

        question = input("Ask a question: ")

        response = await ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            tools=ollama_tools
        )

        tool_calls = response["message"].get("tool_calls", [])

        if not tool_calls:
            print(response["message"]["content"])
            return

        for tc in tool_calls:

            tool_name = tc["function"]["name"]
            tool_args = tc["function"]["arguments"]

            result = await client.call_tool(
                tool_name,
                tool_args
            )

            print("\nTool Selected:")
            print(tool_name)

            print("\nTool Result:")
            print(result.content)

            final = await ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    },
                    {
                        "role": "tool",
                        "name": tool_name,
                        "content": str(result.content)
                    }
                ]
            )

            print("\nFinal Answer:")
            print(final["message"]["content"])


asyncio.run(main())