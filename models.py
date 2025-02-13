import mlx_lm
import logging

class _Model:
    def __init__(self, model_path, custom_model_name):
        if not model_path:
            raise ValueError("model name cannot be empty")
        self.llm_name = model_path
        self.custom_model_name = custom_model_name
        self.model, self.tokenizer = mlx_lm.load(model_path)

    def chat(self, messages, system_prompt=None):
        if system_prompt is not None or system_prompt != "":
            messages.insert(0, {"role": "system", "content": system_prompt})

        if self.tokenizer.chat_template is not None:
            prompt = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)

        logging.debug(f"sending to {self.custom_model_name} {self.llm_name} {messages}")
        logging.debug(f"context size: {len(prompt)} characters")

        return mlx_lm.generate(self.model, self.tokenizer, prompt=prompt, max_tokens=-1)

class DungeonMaster(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.system_prompt = system_prompt

    def chat(self, player_input, scene_summary=None):
        prompt = self.create_prompt(player_input, scene_summary)
        messages = [{"role": "user", "content": prompt}]
        response = super().chat(messages, self.system_prompt)
        return response

    def create_prompt(self, player_input, scene_summary=None):
        if scene_summary is None or scene_summary == "":
            return player_input

        prompt = f"Scene Summary:\n{scene_summary}\n"
        prompt += f"Player Input: {player_input}"
        return prompt

class Summarizer(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.system_prompt = system_prompt

    def chat(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return super().chat(messages, self.system_prompt)

