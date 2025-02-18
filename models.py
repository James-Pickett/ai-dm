import ollama
import logging

class Model:
    def __init__(self, model_path, custom_model_name, options):
        if not model_path:
            raise ValueError("model name cannot be empty")
        self.model_path = model_path
        self.custom_model_name = custom_model_name
        self.options = options

    def chat_stream(self, system_prompt, chat_history_pairs, chat_input):
        messages = []

        if system_prompt and system_prompt != "":
            messages.append({"role": "system", "content": system_prompt})

        for pair in chat_history_pairs:
            messages.append({"role": "user", "content": pair[0]})
            messages.append({"role": "assistant", "content": pair[1]})

        messages.append({"role": "user", "content": chat_input})

        logging.debug(f"sending to {self.custom_model_name} {self.model_path} {messages}")
        response = ollama.chat(model=self.model_path, messages=messages, options=self.options, stream=True)
        for chunk in response:
            yield chunk['message']['content']

    def chat(self, system_prompt, chat_history_pairs, chat_input):
        return "".join(self.chat_stream(system_prompt, chat_history_pairs, chat_input))
