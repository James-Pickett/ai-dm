import ollama
import logging
import json

class Narrator:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized Narrator with model: {model_name}")

    def chat_stream(self, current_input, scene_summary, facts):
        # Start with the system prompt.
        messages = [{"role": "system", "content": self.system_prompt}]

        # Only add scene summary if it is not None and not an empty string.
        if scene_summary is not None and scene_summary.strip():
            messages.append({"role": "user", "content": "describe the scene"})
            messages.append({"role": "assistant", "content": scene_summary})

        if facts is not None and facts:
            messages.append({"role": "user", "content": "extract facts"})
            messages.append({"role": "assistant", "content": json.dumps(facts, indent=4)})

        # Now add the current input.
        messages.append({"role": "user", "content": current_input})

        logging.debug(f"Final Messages Sent to Narrator:\n{json.dumps(messages, indent=4)}")


        response_stream = ollama.chat(model=self.model_name, messages=messages, stream=True)

        full_response = ""
        for chunk in response_stream:
            text_chunk = chunk.get("message", {}).get("content", "")
            full_response += text_chunk
            # Yield each chunk instead of printing it directly.
            yield text_chunk

        logging.debug(f"Full Response: {full_response}")

class Summarizer:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized Summarizer with model: {model_name}")

    def update_scene_summary(self, user_input, narrator_utterance, last_scene_summary=None):
        messages = [{"role": "system", "content": self.system_prompt}]

        content = f"User Utterance: {user_input}\nNarrator Utterance: {narrator_utterance}"
        if last_scene_summary:
            content = f"{last_scene_summary}\n{content}"

        messages.append({"role": "user", "content": content})

        logging.debug(f"Final Messages Sent to Summarizer:\n{json.dumps(messages, indent=4)}")

        try:
            response = ollama.chat(model=self.model_name, messages=messages, stream=False)
            response_text = response.get("message", {}).get("content", "")
            logging.debug(f"Full Response: {response_text}")
            return response_text
        except Exception as e:
            logging.error(f"Error in chat response: {e}")
            return "An error occurred while processing the request."

class Factualizer:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized Factualizer with model: {model_name}")

    def update_facts(self, narrartor_utterance):
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": narrartor_utterance})

        logging.debug(f"Final Messages Sent to Factualizer:\n{json.dumps(messages, indent=4)}")

        try:
            response = ollama.chat(model=self.model_name, messages=messages, stream=False)
            response_text = response.get("message", {}).get("content", "")
            logging.debug(f"Full Response: {response_text}")
            return response_text
        except Exception as e:
            logging.error(f"Error in chat response: {e}")
            return "An error occurred while processing the request."
