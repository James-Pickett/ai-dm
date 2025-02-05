import ollama
import logging
import json

class OllamaModel:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized OllamaModel with model: {model_name}")

    def chat(self, current_input, previous_inputs=[]):
        logging.debug(f"Current input: {current_input}")
        logging.debug(f"Previous inputs: {previous_inputs}")

        # Construct the message history
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add previous inputs in alternating roles
        for entry in previous_inputs:
            messages.append({"role": "user", "content": entry["user"]})
            if "assistant" in entry:
                messages.append({"role": "assistant", "content": entry["assistant"]})

        # Append the current player input
        messages.append({"role": "user", "content": current_input})

        print(json.dumps(messages, indent=4))  # Debugging JSON format

        # Send to Ollama with streaming enabled
        response_stream = ollama.chat(model=self.model_name, messages=messages, stream=True)

        return response_stream  # Return the generator for streaming
