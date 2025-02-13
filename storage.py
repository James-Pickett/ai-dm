import os

def save_scene_summary(summary):
    # Ensure the directory exists
    os.makedirs('./game_data', exist_ok=True)

    # Save the summary to the file
    with open('./game_data/scene_summary.txt', 'w') as file:
        file.write(summary)
