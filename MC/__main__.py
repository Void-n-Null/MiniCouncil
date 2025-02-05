# Entry point for the Mini Council

from MC.openrouter_client import OpenRouterClient, Message
from MC.tools.registry import registry
import json
import asyncio

def get_current_time():
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_file(path: str):
    """Read contents of a file."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return f"Error: File {path} not found"

def write_file(path: str, content: str):
    """Write content to a file."""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

# Define available tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]

async def handle_tool_call(tool_call):
    """Handle a tool call from the model."""
    function_name = tool_call['function']['name']
    try:
        arguments = json.loads(tool_call['function']['arguments'])
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in arguments for {function_name}"
    
    try:
        # Get the tool class from registry
        tool_class = registry.get_tool(function_name)
        # Create an instance and execute
        tool = tool_class()
        result = await tool.execute(**arguments)
        return json.dumps(result) if isinstance(result, dict) else str(result)
    except KeyError:
        return f"Error: Unknown function {function_name}"
    except Exception as e:
        return f"Error executing {function_name}: {str(e)}"

async def main():
    # Initialize the client
    client = OpenRouterClient()
    
    # Create a message that demonstrates multiple tool uses
    messages = [
        Message(role="user", content="""
        1. Get the current time
        2. Create a file called 'current_time.txt' with that time
        3. Read back the contents of the file to verify
        4. Get the time in a different format (just the date)
        """)
    ]
    
    while True:
        # Get completion from model with tools
        response = client.chat_completion(
            messages=messages,
            model="openai/gpt-3.5-turbo",
            tools=registry.get_tool_schemas(),
            temperature=0.7
        )
        
        message = response['choices'][0]['message']
        
        # If the model wants to use tools
        if 'tool_calls' in message:
            for tool_call in message['tool_calls']:
                result = await handle_tool_call(tool_call)
                
                # Add the tool call to messages
                messages.append(Message(
                    role="assistant",
                    content=None,
                    tool_calls=[tool_call]
                ))
                
                # Add the tool result to messages
                messages.append(Message(
                    role="tool",
                    content=result,
                    name=tool_call['function']['name'],
                    tool_call_id=tool_call['id']
                ))
            
            # Continue the conversation with the tool results
            continue
        
        # If no more tool calls, print the final response
        print("\nFinal Response:")
        print(message['content'])
        break

if __name__ == "__main__":
    print("Starting Mini Council demo...")
    print("This example will:")
    print("1. Get the current time")
    print("2. Save it to a file")
    print("3. Read it back")
    print("4. Get the time in a different format")
    print("\nWatching the AI use tools to accomplish this...\n")
    
    asyncio.run(main())

