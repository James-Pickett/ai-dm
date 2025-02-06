import ollama
import logging
import json

class OllamaModel:
    def __init__(self, model_name, system_prompt):
        self.model_name = model_name
        self.system_prompt = system_prompt
        logging.debug(f"Initialized OllamaModel with model: {model_name}")

    def chat_stream(self, current_input, scene_summary=None):
        """
        Handles streaming responses for real-time narration.
        Instead of printing output, yields each text chunk.
        The message order is:
          1. System prompt.
          2. If provided and non-empty, scene summary context:
             - user: "describe the scene"
             - assistant: scene_summary
          3. Current input.
        """
        logging.debug(f"Current input: {current_input}")
        logging.debug(f"Scene summary: {scene_summary}")

        # Start with the system prompt.
        messages = [{"role": "system", "content": self.system_prompt}]

        # Only add scene summary if it is not None and not an empty string.
        if scene_summary is not None and scene_summary.strip():
            messages.append({"role": "user", "content": "describe the scene"})
            messages.append({"role": "assistant", "content": scene_summary})

        # Now add the current input.
        messages.append({"role": "user", "content": current_input})

        logging.debug(f"Final Messages Sent to Model:\n{json.dumps(messages, indent=4)}")

        try:
            # Stream response from Ollama
            response_stream = ollama.chat(model=self.model_name, messages=messages, stream=True)

            full_response = ""
            for chunk in response_stream:
                text_chunk = chunk.get("message", {}).get("content", "")
                full_response += text_chunk
                # Yield each chunk instead of printing it directly.
                yield text_chunk

            logging.debug(f"Full Response: {full_response}")
        except Exception as e:
            logging.error(f"Error in chat response: {e}")
            # Yield an error message so that main.py can handle it.
            yield "An error occurred while processing the request."

    def chat(self, current_input, scene_summary=None):
        """
        Handles regular (non-streaming) responses, useful for summarization.
        The message order is:
          1. System prompt.
          2. If provided and non-empty, scene summary context:
             - user: "describe the scene"
             - assistant: scene_summary
          3. Current input.
        """
        logging.debug(f"Current input: {current_input}")
        logging.debug(f"Scene summary: {scene_summary}")

        messages = [{"role": "system", "content": self.system_prompt}]

        if scene_summary is not None and scene_summary.strip():
            messages.append({"role": "user", "content": "describe the scene"})
            messages.append({"role": "assistant", "content": scene_summary})

        messages.append({"role": "user", "content": current_input})

        logging.debug(f"Final Messages Sent to Model:\n{json.dumps(messages, indent=4)}")

        try:
            response = ollama.chat(model=self.model_name, messages=messages, stream=False)
            response_text = response.get("message", {}).get("content", "")
            logging.debug(f"Full Response: {response_text}")
            return response_text
        except Exception as e:
            logging.error(f"Error in chat response: {e}")
            return "An error occurred while processing the request."
