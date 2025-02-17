import ollama
import logging

class _Model:
    def __init__(self, model_path, custom_model_name, system_prompt, options):
        if not model_path:
            raise ValueError("model name cannot be empty")
        self.model_path = model_path
        self.custom_model_name = custom_model_name
        self.system_prompt = system_prompt
        self.options = options

    def generate_stream(self, messages):
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        logging.debug(f"sending to {self.custom_model_name} {self.model_path} {messages}")

        response = ollama.chat(model=self.model_path, messages=messages, options=self.options, stream=True)

        for chunk in response:
            yield chunk['message']['content']

    def generate(self, messages):
        return "".join(self.generate_stream(messages))

class GameMaster(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt, options):
        super().__init__(model_path, custom_model_name, system_prompt, options)

    def chat_stream(self, input):
        messages = [{"role": "user", "content": input}]
        return super().generate_stream(messages)

class NoteTaker(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt, options):
        super().__init__(model_path, custom_model_name, system_prompt, options)

    def chat(self, input):
        messages = [{"role": "user", "content": input}]
        return super().generate(messages)
