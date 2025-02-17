import config
import models
import my_logging
import storage
import prompt_builder

def init_game_master(config):
    game_master_model = config.get("game_master_model")
    model_path = game_master_model["model_path"]
    system_prompt = game_master_model["system_prompt"]
    options = game_master_model.get("model-args", {})

    if not model_path:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.GameMaster(model_path, "Game Master", system_prompt, options)

def init_note_taker(config):
    note_taker_model = config.get("note_taker_model")
    model_name = note_taker_model["model_path"]
    system_prompt = note_taker_model["system_prompt"]
    options = note_taker_model.get("model-args", {})

    if not model_name:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.NoteTaker(model_name, "Note Taker", system_prompt, options)

if __name__ == '__main__':
    my_logging.setup()

    config = config.load('./config.yml')
    game_master = init_game_master(config)
    note_taker = init_note_taker(config)

    gamemaster_logger = my_logging.MyModelLogger("game_master")
    note_taker_logger = my_logging.MyModelLogger("note_taker")

    current_notes = storage.load_game_notes()
    last_game_master_response = ""

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        print("\n ---------- \n")

        vector_search_results = storage.search_vector_db(user_input + current_notes + last_game_master_response)
        gamemaster_input = prompt_builder.gamemaster_prompt(user_input, current_notes, vector_search_results)

        # Stream the game master's response to the terminal.
        last_game_master_response = ""
        print("Game Master: ", end="", flush=True)
        for token in game_master.chat_stream(gamemaster_input):
            last_game_master_response += token
            print(token, end="", flush=True)

        print("\n\n ========== \n")
        gamemaster_logger.log(gamemaster_input, last_game_master_response)

        # get note takers ouput
        notetaker_input = prompt_builder.notetaker_prompt(user_input, last_game_master_response)
        new_game_notes = note_taker.chat(notetaker_input)
        note_taker_logger.log(notetaker_input, new_game_notes)

        current_notes = new_game_notes
        storage.save_game_notes(current_notes)
        storage.save_to_vector_db(current_notes)
