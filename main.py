import config
import models
import my_logging
import storage
import prompt_builder

def init_model(config, log_component: my_logging.Component, model_config_name):
    model = config.get(model_config_name)
    model_path = model["model_path"]
    options = model.get("model-args", {})

    if not model_path:
        raise ValueError("model path cannot be empty")

    return models.Model(log_component, model_path, options)

def extract_between_tags(text, start_tag, end_tag):
    start_index = text.find(start_tag) + len(start_tag)
    end_index = text.find(end_tag)

    if end_index == -1:
        end_index = len(text)

    return text[start_index:end_index].strip() if start_index != -1 and end_index != -1 else ""

if __name__ == '__main__':
    config = config.load('./config.yml')

    game_master = init_model(config, my_logging.Component.GAME_MASTER_RAW, "game_master_model")
    fact_extractor = init_model(config, my_logging.Component.FACT_EXTRACTOR_RAW, "fact_extractor_model")
    scene_note_taker = init_model(config, my_logging.Component.SCENE_NOTE_TAKER_RAW, "scene_note_taker_model")

    gamemaster_transcript_saver = storage.TranscriptSaver(my_logging.Component.GAME_MASTER, data_dir="./game_data")

    current_scene_notes = storage.load_scene_notes()
    last_game_master_response = ""

    while True:
        player_input = input("You: ").strip()
        if player_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        print("\n ---------- \n")

        vector_search_results = storage.search_vector_db(f"{player_input} {current_scene_notes} {last_game_master_response}", 20)

        gamemaster_system_prompt = prompt_builder.gamemaster_system_prompt()
        gamemaster_chat_history = gamemaster_transcript_saver.get_last_n_pairs(5)
        game_master_prompt = prompt_builder.gamemaster_prompt(scene_notes=current_scene_notes, campaign_facts=vector_search_results, player_input=player_input)

        # Stream the game master's response to the terminal.
        last_game_master_response = ""
        print("Game Master: ", end="", flush=True)
        for token in game_master.chat_stream(gamemaster_system_prompt, gamemaster_chat_history, game_master_prompt):
            last_game_master_response += token
            print(token, end="", flush=True)

        print("\n\n ========== \n")
        gamemaster_transcript_saver.save_to_transcript(game_master_prompt, last_game_master_response)

        # get note takers ouput
        fact_extractor_prompt = prompt_builder.fact_extractor_prompt(player_input, last_game_master_response)
        new_facts = fact_extractor.chat(prompt_builder.fact_extractor_system_prompt(), [], fact_extractor_prompt)

        new_facts = extract_between_tags(new_facts, "<facts>", "</facts>")
        if not new_facts or new_facts == "":
            print("ERROR: No new facts found.")
        else:
            storage.save_to_vector_db(new_facts)

        scene_note_taker_system_prompt = prompt_builder.scene_note_taker_system_prompt()
        scene_note_taker_prompt = prompt_builder.scene_note_taker_prompt(current_scene_notes, player_input, last_game_master_response)
        scene_note_taker_response = scene_note_taker.chat(scene_note_taker_system_prompt, [], scene_note_taker_prompt)

        scene_note_taker_response = extract_between_tags(scene_note_taker_response, "<updated_scene_notes>", "</updated_scene_notes>")
        if not scene_note_taker_response or scene_note_taker_response == "":
            print("ERROR: No new scene notes found.")
        else:
            current_scene_notes = scene_note_taker_response
            storage.save_game_notes(current_scene_notes)



