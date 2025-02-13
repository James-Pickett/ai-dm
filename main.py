import config
import models
import my_logging
import storage

def init_dungeon_master(config):
    model_name = config.get("dungeon_master_model")
    system_prompt = config.get("dungeon_master_system_prompt")

    if not model_name:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.DungeonMaster(model_name, "Dungeon Master", system_prompt)

def init_summarizer(config):
    model_name = config.get("summarizer_model")
    system_prompt = config.get("summarizer_system_prompt")

    if not model_name:
        raise ValueError("model name cannot be empty")

    if not system_prompt:
        raise ValueError("system prompt cannot be empty")

    return models.Summarizer(model_name, "Summarizer", system_prompt)

if __name__ == '__main__':
    my_logging.setup()

    config = config.load('./config.yml')
    dungeon_master = init_dungeon_master(config)
    summarizer = init_summarizer(config)

    scene_summary = storage.load_scene_summary()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        response = dungeon_master.chat(user_input, scene_summary)
        print("Dungeon Master:", response)

        new_scene_summary = summarizer.chat(response)
        scene_summary = new_scene_summary
        storage.save_scene_summary(scene_summary)
