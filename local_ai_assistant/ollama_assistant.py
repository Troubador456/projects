import ollama

def run_assistant():
    response = ollama.list()
    for model in response.get('models', []):
        name = model.get('model')
        size_gb = model.get('size', 0) / (1024 ** 3)
        print(f"- {name} ({size_gb:.2f} GB)")
    selected_ollama_model = input("Your selected model?: ")
    '''
    ollama = load_ollama()
    if ollama is None:
        print("The ollama package is not installed.")
        return
    print("ollama is available")
    '''
    print("Local AI Assistant is ready! Type 'exit' to quit.\n")

    conversation_history = [
        {"role": "system", "content": "You are a helpful, concise local AI assistant"}
    ]
    
    while True:
        user_input = input()
        if user_input.lower() in ['exit', 'goodbye', 'bye', 'adieu', 'bye bye', 'farewell', 'see you', 'see ya', 'take care']:
            break
        conversation_history.append({"role": "user", "content": user_input})

        try:

            stream = ollama.chat(
                model=selected_ollama_model,
                messages=conversation_history,
                stream=True
            )

            print("AI: ", end="", flush=True)
            assistant_response = ""

            for chunk in stream:
                content = chunk['message']['content']
                print(content, end="", flush=True)
                assistant_response+=content
            print("\n")

            conversation_history.append({"role": "assistant", "content": assistant_response})
        except Exception as e:
            print(f"\nError connecting... : {e}")
if __name__ == "__main__":
    run_assistant()
