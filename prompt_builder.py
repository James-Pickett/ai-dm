def gamemaster_prompt(player_input, game_notes, vector_search_results):
    if game_notes is None or game_notes == "":
        return f"Lets start the scene, here is the player input:\n---\n{player_input}"

    prompt = f"Please continue the scene from these notes:\n---\n{game_notes}\n---\n\n"

    if vector_search_results is not None and vector_search_results != "":
        prompt += f"Here is some additional information about the overall campaign:\n---\n{vector_search_results}\n---\n\n"

    prompt += "The player is aware of the notes, no need to repeat them or reset the scene unless asked.\n\n"
    prompt += f"Here is the player input:\n---\n{player_input}"
    return prompt

def notetaker_prompt(player_input, game_master_output):
    prompt = "Please extract facts from the player's and gamemaster's output.\n"
    prompt += f"Here is the player input:\n---\n{player_input}\n---\n\n"
    prompt += f"Here is the game master's output:\n---\n{game_master_output}"
    return prompt
