"""Main Module - Entry point for the Mini Council application.

This module:
- Initializes the CLI and Agent components
- Sets up the tool improvement process
- Manages the main application flow
- Handles user interaction
"""

import asyncio
from .cli import CLI
from .core.agent import Agent

async def main():
    """Run the main application loop."""
    # Initialize components
    cli = CLI()
    agent = Agent(
        name="ToolImprover",
        model="google/gemini-2.0-flash-001",
        tools=["read_file", "write_file"]  # Only use file-related tools
    )
    
    # Display welcome message
    print("Starting Tool Improvement Process...")
    print("1. Reading current tool implementation")
    print("2. Analyzing for potential improvements")
    print("3. Writing recommendations")
    print("4. Implementing improvements")
    print("\nWatching the AI analyze and improve itself...\n")
    
    # Define the analysis prompt
    analysis_prompt = """
    1. Read the contents of 'MC/tools/file_tools.py'
    2. Analyze the current implementation of ReadFileTool and WriteFileTool
    3. Create a file called 'tool_improvements.txt' with detailed recommendations for improvements
    4. Read back the recommendations
    5. Create a new file called 'improved_file_tools.py' with the improved implementation
    
    Please be specific and thorough in your analysis and improvements.
    Consider edge cases, error handling, and user experience.
    """
    
    # Add the initial message and get response
    agent.add_message(analysis_prompt)
    final_response = await agent.get_response()
    
    # Display the final response
    cli.print_final_response(final_response)

if __name__ == "__main__":
    asyncio.run(main())

