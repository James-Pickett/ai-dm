import config
import models
import my_logging
import storage

def init_game_master(config):
    model_name = config.get("game_master_model")
    system_prompt = config.get("game_master_system_prompt")

    if not model_name:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.GameMaster(model_name, "Game Master", system_prompt)

def init_note_taker(config):
    model_name = config.get("note_taker_model")
    system_prompt = config.get("note_taker_system_prompt")

    if not model_name:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.NoteTaker(model_name, "Note Taker", system_prompt)

if __name__ == '__main__':
    my_logging.setup()

    config = config.load('./config.yml')
    game_master = init_game_master(config)
    note_taker = init_note_taker(config)

    current_notes = storage.load_game_notes()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        print("\n ---------- \n")

        # Stream the game master's response to the terminal.
        print("Game Master: ", end="", flush=True)
        game_master_response = ""
        for token in game_master.chat_stream(user_input, current_notes):
            game_master_response += token
            print(token, end="", flush=True)

        print("\n\n ========== \n")

        new_game_notes = note_taker.chat(current_notes, user_input, game_master_response)
        current_notes = new_game_notes
        storage.save_game_notes(current_notes)
