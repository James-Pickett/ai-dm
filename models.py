import mlx_lm
import logging

class _Model:
    def __init__(self, model_name):
        if not model_name:
            raise ValueError("model name cannot be empty")
        self.model, self.tokenizer = mlx_lm.load(model_name)

    def chat(self, messages):
        if self.tokenizer.chat_template is not None:
            prompt = self.tokenizer.apply_chat_template(
                messages, add_generation_prompt=True
            )

        return mlx_lm.generate(self.model, self.tokenizer, prompt=prompt, max_tokens=-1)

class DungeonMaster(_Model):
    def __init__(self, model_name):
        super().__init__(model_name)
        self.chat_history = []

    def chat(self, prompt):
        self.chat_history.append({"role": "user", "content": prompt})
        response = super().chat(self.chat_history)
        self.chat_history.append({"role": "assistant", "content": response})
        return response

