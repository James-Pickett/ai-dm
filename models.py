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
            return f"Lets start the scene, here is the player input\n---\n{player_input}\n---\n"

        prompt = f"Please continue the scene from these notes\n---\n{game_notes}\n---\n"
        prompt += "The player is aware of the notes, no need to repeat them or reset the scene unless asked.\n"
        prompt += f"Here is the player input\n---\n{player_input}\n---\n"
        return prompt

class NoteTaker(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name, system_prompt)

    def chat(self, player_input, game_master_response, game_notes):
        prompt = self.create_prompt(player_input, game_master_response, game_notes)
        messages = [{"role": "user", "content": prompt}]
        return super().generate(messages)

    def create_prompt(self, game_notes, player_input, game_master_response):
        prompt = f"Take notes on the current scene\n---\nHere is the players input\n---\n{player_input}\n---\n"
        prompt += f"Here is the game master's response\n---\n{game_master_response}\n---\n"

        if game_notes is None or game_notes == "":
            return prompt

        prompt += f"Here are your last notes on the current scene\n---\n{game_notes}\n---\n"
        return prompt



