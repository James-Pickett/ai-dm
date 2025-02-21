import ollama
import my_logging
import os
import yaml

MODEL_TRANSCRIPT_DEBUG_PATH = "./debug/model_transcrpt.yml"
os.makedirs("./debug", exist_ok=True)

class Model:
    def __init__(self, log_component: my_logging.Component, model_path, options):
        if not model_path:
            raise ValueError("model path cannot be empty")

        self.model_path = model_path
        self.options = options
        self.logger = my_logging.get_logger(log_component)
        self.component = log_component

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

        # will need to remove this later, this just makes it easier to see the input/output of the model
        model_transript_obj = {
            "component": self.component.value,
            "model_path": self.model_path,
            "messages": messages
        }

        with open(MODEL_TRANSCRIPT_DEBUG_PATH, "a") as f:
            f.write("\n---\n")
            yaml.dump(model_transript_obj, f, default_style="|")

    def chat(self, system_prompt, chat_history_pairs, chat_input):
        return "".join(self.chat_stream(system_prompt, chat_history_pairs, chat_input))
