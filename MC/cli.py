class CLI:
    """Handles command-line interface concerns."""
    
    @staticmethod
    def print_welcome_message() -> None:
        """Print the welcome message and instructions."""
        print("Starting Mini Council demo...")
        print("This example will:")
        print("1. Come up with 5 dad jokes")
        print("2. Create a file called 'jokes.txt' with the jokes")
        print("3. Read back the contents of the file")
        print("4. Get the jokes in a different format")
        print("\nWatching the AI use tools to accomplish this...\n")
    
    @staticmethod
    def print_final_response(response: str) -> None:
        """Print the final response from the conversation."""
        print("\nFinal Response:")
        print(response) 