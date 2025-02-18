import ollama
import my_logging

class Model:
    def __init__(self, log_component: my_logging.Component, model_path, options):
        if not model_path:
            raise ValueError("model name cannot be empty")

        self.model_path = model_path
        self.options = options
        self.logger = my_logging.get_logger(log_component)

    def chat_stream(self, system_prompt, chat_history_pairs, chat_input):
        messages = []

        if system_prompt and system_prompt != "":
            messages.append({"role": "system", "content": system_prompt})

        for pair in chat_history_pairs:
            messages.append({"role": "user", "content": pair[0]})
            messages.append({"role": "assistant", "content": pair[1]})

        messages.append({"role": "user", "content": chat_input})

        response = ollama.chat(model=self.model_path, messages=messages, options=self.options, stream=True)
        responseStr = ""
        for chunk in response:
            responseStr += chunk['message']['content']
            yield chunk['message']['content']

        messages.append({"role": "assistant", "content": responseStr})
        self.logger.debug(
            "interaction with model",
            extra=
            {
                "model_path": self.model_path,
                "messages": messages,
            }
        )

    def chat(self, system_prompt, chat_history_pairs, chat_input):
        return "".join(self.chat_stream(system_prompt, chat_history_pairs, chat_input))
