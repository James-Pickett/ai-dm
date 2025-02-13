import os

SCENE_SUMMARY_PATH = './game_data/scene_summary.txt'

def save_scene_summary(summary):
    os.makedirs(os.path.dirname(SCENE_SUMMARY_PATH), exist_ok=True)
    with open(SCENE_SUMMARY_PATH, 'w') as file:
        file.write(summary)

def load_scene_summary():
    if not os.path.exists(SCENE_SUMMARY_PATH):
        return ""

    with open(SCENE_SUMMARY_PATH, 'r') as file:
        return file.read()
