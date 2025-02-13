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
        if system_prompt is not None:
            messages.insert(0, {"role": "system", "content": system_prompt})

        logging.debug(f"sending to {self.custom_model_name} {self.llm_name} {messages}")

        if self.tokenizer.chat_template is not None:
            prompt = self.tokenizer.apply_chat_template(
                messages, add_generation_prompt=True
            )

        return mlx_lm.generate(self.model, self.tokenizer, prompt=prompt, max_tokens=-1)

class DungeonMaster(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.chat_history = []
        self.system_prompt = system_prompt

    def chat(self, prompt):
        self.chat_history.append({"role": "user", "content": prompt})
        response = super().chat(self.chat_history.copy(), self.system_prompt)
        self.chat_history.append({"role": "assistant", "content": response})
        return response

class Summarizer(_Model):
    def __init__(self, model_path, custom_model_name, system_prompt):
        super().__init__(model_path, custom_model_name)
        self.system_prompt = system_prompt

    def chat(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        return super().chat(messages, self.system_prompt)

