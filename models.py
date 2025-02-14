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

    def chat_stream(self, player_input, game_notes):
        prompt = self.create_prompt(player_input, game_notes)
        messages = [{"role": "user", "content": prompt}]
        return super().generate_stream(messages)

    def create_prompt(self, player_input, game_notes):
        if game_notes is None or game_notes == "":
            return player_input

        prompt = f"Game Notes:\n{game_notes}\n"
        prompt += f"Player Input:\n{player_input}"
        return prompt

class NoteTaker(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name, system_prompt)

    def chat(self, player_input, game_master_response, game_notes):
        prompt = self.create_prompt(player_input, game_master_response, game_notes)
        messages = [{"role": "user", "content": prompt}]
        return super().generate(messages)

    def create_prompt(self, game_notes, player_input, game_master_response):
        prompt = f"Player Input:\n{player_input}\nGame Master Response:\n{game_master_response}"

        if game_notes is None or game_notes == "":
            return prompt

        return f"Game Notes:\n{game_notes}\n{prompt}"



