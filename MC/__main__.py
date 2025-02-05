# Entry point for the Mini Council

from MC.openrouter_client import OpenRouterClient, Message

def main():
    # Initialize the client
    client = OpenRouterClient()
    
    # Create a message
    messages = [
        Message(role="user", content="Say this is a test")
    ]
    
    # Get completion from o3-mini model
    response = client.chat_completion(
        messages=messages,
        model="openai/o3-mini",  # Using the o3-mini model
        temperature=0.7
    )
    
    # Print the response
    print(response['choices'][0]['message']['content'])

if __name__ == "__main__":
    main()

