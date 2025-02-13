import config
import models
import my_logging

if __name__ == '__main__':
    my_logging.setup()

    config = config.load('./config.yml')

    dungeon_master = models.DungeonMaster(config.get("dungeon_master_model"))

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        # Get the response from the dungeon master model and print it
        response = dungeon_master.chat(user_input)
        print("Dungeon Master:", response)
