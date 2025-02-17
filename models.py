import ollama
import logging

class _Model:
    def __init__(self, model_path, custom_model_name, system_prompt):
        if not model_path:
            raise ValueError("model name cannot be empty")
        self.model_path = model_path
        self.custom_model_name = custom_model_name
        self.system_prompt = system_prompt

    def generate_stream(self, messages):
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        logging.debug(f"sending to {self.custom_model_name} {self.model_path} {messages}")

        options = {
            "temperature": 0.8,
            "repeat_penalty": 1.05,
            "min_p": 0.025,
            "num_ctx": 32768,
        }

        response = ollama.chat(model=self.model_path, messages=messages, options=options, stream=True)

        for chunk in response:
            yield chunk['message']['content']

    def generate(self, messages):
        return "".join(self.generate_stream(messages))

class GameMaster(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name, system_prompt)

    def chat_stream(self, input):
        messages = [{"role": "user", "content": input}]
        return super().generate_stream(messages)

class NoteTaker(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name, system_prompt)

    def chat(self, input):
        messages = [{"role": "user", "content": input}]
        return super().generate(messages)
