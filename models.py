import mlx_lm
import logging

class _Model:
    def __init__(self, model_path, custom_model_name):
        if not model_path:
            raise ValueError("model name cannot be empty")
        self.model_path = model_path
        self.custom_model_name = custom_model_name
        self.model, self.tokenizer = mlx_lm.load(model_path)

    def chat(self, messages, system_prompt=None):
        if system_prompt is not None or system_prompt != "":
            messages.insert(0, {"role": "system", "content": system_prompt})

        if self.tokenizer.chat_template is not None:
            prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)

        logging.debug(f"sending to {self.custom_model_name} {self.model_path} {messages}")
        logging.debug(f"context size: {len(prompt)} characters")

        return mlx_lm.generate(self.model, self.tokenizer, prompt=prompt, max_tokens=5000)

class DungeonMaster(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.system_prompt = system_prompt

    def chat(self, player_input, game_notes):
        prompt = self.create_prompt(player_input, game_notes)
        messages = [{"role": "user", "content": prompt}]
        response = super().chat(messages, self.system_prompt)
        return response

    def create_prompt(self, player_input, game_notes):
        if game_notes is None or game_notes == "":
            return player_input

        prompt = f"Game Notes:\n{game_notes}\n"
        prompt += f"Player Input:\n{player_input}"
        return prompt

class NoteTaker(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.system_prompt = system_prompt

    def chat(self, player_input, dungeon_master_response, game_notes):
        prompt = self.create_prompt(player_input, dungeon_master_response, game_notes)
        messages = [{"role": "user", "content": prompt}]
        return super().chat(messages, self.system_prompt)

    def create_prompt(self, game_notes, player_input, dungeon_master_response):
        prompt = f"Player Input:\n{player_input}\nDungeon Master Response:\n{dungeon_master_response}"

        if game_notes is None or game_notes == "":
            return prompt

        return f"Game Notes:\n{game_notes}\n{prompt}"



