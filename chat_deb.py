import ollama

class OllamaChat:
    def __init__(self, system_prompt, model="llama3.2"):
        self.model = model
        self.history = [{
            "role": "system",
            "content": system_prompt
        }]

    def generate_response(self, prompt):
        try:
            # Using stream=True for streaming responses
            response_stream = ollama.chat(
                model=self.model,
                messages=self.history + [{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Initialize full response content
            full_response = ""
            print(f"\n{self.model}: ", end="", flush=True)
            
            # Process the stream
            for chunk in response_stream:
                chunk_content = chunk['message']['content']
                print(chunk_content, end="", flush=True)
                full_response += chunk_content
                
            print()  # New line after response
            return full_response
            
        except Exception as e:
            return f"Error: {str(e)}"

    def load_chat_history(self, filename):
        """Load chat history from a text file in the format:
        You: message
        llama3.2: response
        """
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            # Preserve system prompt
            system_prompt = self.history[0]
            self.history = [system_prompt]
            
            current_message = ""
            for line in lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                if line.startswith("You: "):
                    # Add the previous message if exists
                    if current_message:
                        self.history.append({
                            "role": "assistant",
                            "content": current_message.strip()
                        })
                    # Start new user message
                    current_message = line[5:]  # Remove "You: "
                    self.history.append({
                        "role": "user",
                        "content": current_message.strip()
                    })
                    current_message = ""
                elif line.startswith(f"{self.model}: "):
                    # Add the previous message if exists
                    if current_message:
                        self.history.append({
                            "role": "user",
                            "content": current_message.strip()
                        })
                    # Start new assistant message
                    current_message = line[len(f"{self.model}: "):]  # Remove "model: "
                    
            # Add the last message if exists
            if current_message:
                self.history.append({
                    "role": "assistant",
                    "content": current_message.strip()
                })
                
            print(f"Chat history loaded from {filename}")
            return True
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            return False

    def chat(self):
        print(f"Chat with {self.model} (type 'quit' to exit)")
        print("-" * 50)

        # Ask user if they want to load previous chat history
        load_history = input("Would you like to load previous chat history? (y/n): ").strip().lower()
        if load_history == 'y':
            filename = input("Enter the path to your chat history text file: ").strip()
            self.load_chat_history(filename)

        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("\nGoodbye!")
                break
            
            if user_input:
                self.history.append({"role": "user", "content": user_input})
                response = self.generate_response(user_input)
                self.history.append({"role": "assistant", "content": response})

def main():
    # Example of a custom system prompt
    custom_prompt = """You are a debate focused AI whose job is to challenge my arguments, present strong counterarguments, and clearly point out any logical fallacies or weak assumptions. Maintain a firm, rational, and respectful tone. Do not simply agree—critique, question, and push the reasoning deeper. When you identify a flaw, name the fallacy and briefly explain why it applies. Keep responses concise, focused, and intellectually rigorous. Always maintain confidentiality and respect throughout our conversations."""
    
    chat_bot = OllamaChat(
    	system_prompt=custom_prompt,
        model="llama3.2"
    )
    chat_bot.chat()

if __name__ == "__main__":
    main()
