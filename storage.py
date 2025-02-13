import os

GAME_NOTES_PATH = './game_data/game_notes.txt'

def save_game_notes(notes):
    os.makedirs(os.path.dirname(GAME_NOTES_PATH), exist_ok=True)
    with open(GAME_NOTES_PATH, 'w') as file:
        file.write(notes)

def load_game_notes():
    if not os.path.exists(GAME_NOTES_PATH):
        return ""

    with open(GAME_NOTES_PATH, 'r') as file:
        return file.read()
