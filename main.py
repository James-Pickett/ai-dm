import config
import models
import my_logging
import storage
import prompt_builder

def init_model(config, log_component: my_logging.Component, model_config_name):
    game_master_model = config.get(model_config_name)
    model_path = game_master_model["model_path"]
    options = game_master_model.get("model-args", {})

    if not model_path:
        raise ValueError("model path cannot be empty")

    return models.Model(log_component, model_path, options)

if __name__ == '__main__':
    config = config.load('./config.yml')
    game_master = init_model(config, my_logging.Component.GAME_MASTER_RAW, "game_master_model")
    note_taker = init_model(config, my_logging.Component.NOTE_TAKER_RAW, "note_taker_model")

    gamemaster_transcript_saver = storage.TranscriptSaver(my_logging.Component.GAME_MASTER, data_dir="./game_data")

    current_notes = storage.load_game_notes()
    last_game_master_response = ""

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        print("\n ---------- \n")

        vector_search_results = storage.search_vector_db(f"{user_input} {current_notes} {last_game_master_response}", 20)

        gamemaster_system_prompt = prompt_builder.gamemaster_system_prompt(current_notes, vector_search_results)
        gamemaster_chat_history = gamemaster_transcript_saver.get_last_n_pairs(5)

        # Stream the game master's response to the terminal.
        last_game_master_response = ""
        print("Game Master: ", end="", flush=True)
        for token in game_master.chat_stream(gamemaster_system_prompt, gamemaster_chat_history, user_input):
            last_game_master_response += token
            print(token, end="", flush=True)

        print("\n\n ========== \n")
        gamemaster_transcript_saver.save_to_transcript(user_input, last_game_master_response)

        # get note takers ouput
        notetaker_input = prompt_builder.notetaker_prompt(user_input, last_game_master_response)
        new_game_notes = note_taker.chat(prompt_builder.notetaker_system_prompt(), [], notetaker_input)

        current_notes = new_game_notes
        storage.save_game_notes(current_notes)
        storage.save_to_vector_db(current_notes)
