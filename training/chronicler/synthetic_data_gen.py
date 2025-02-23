from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List

from langchain.output_parsers import PydanticOutputParser, RetryOutputParser
from langchain_ollama.llms import OllamaLLM

class SceneNotes(BaseModel):
    player_characters: List[str] = Field(
        description="List of player characters in the scene",
    )
    non_player_characters: List[str] = Field(
        description="List of non-player characters in the scene",
    )
    players_characters_location: List[str] = Field(
        description="The players location from largest to smallest (e.g. region, city, building, room)",
    )
    scene_details: List[str] = Field(
        description="Very detailed transient details of specific scene such as weather, mood, smells, sounds, character interactions, etc.",
    )

class ChroniclerOutput(BaseModel):
    scene_notes: SceneNotes = Field(
        description="Secene notes created or updated based on the player and dungeon master utterances",
    )
    campaign_facts: List[str] = Field(
        description="List of independent facts extracted from the player and game master utterances. The are facts that a relevant to the entire campaign rather than a single scene. These facts must make sense without the context of the utterances, scene notes, or other facts. Facts should NEVER include minor details or transient information. Facts should be relevant to the campaign and the characters, locations, and items in it. Facts should be written in complete sentences. Each fact should have a high likelihood of being true a month from now. Each fact must include a proper name or noun for a person, place, or thing.",
    )

class ChroniclerInput(BaseModel):
    player_utterance: str = Field(
        description="Something a player might say during a TTRPG campaign",
    )
    game_master_utterance: str = Field(
        description="Something a dungeon master might say during a TTRPG campaign. Proper names and nouns should be used whenever possible",
    )

class ChroniclerTrainingEntry(BaseModel):
    chronicler_input: ChroniclerInput = Field(
        description="The input the chronicler would receive from the player and dungeon master",
    )
    chronicler_output: ChroniclerOutput = Field(
        description="The output the chronicler would generate based on the input",
    )

model = OllamaLLM(model="mistral:7b-instruct", temperature=1, num_ctx=32000)

class Generator:
    def __init__(self):
        self.model_path = OllamaLLM(model="mistral:7b-instruct", temperature=1, num_ctx=32000)

    def generate(self, prompt_template, pydantic_object, examples, count=1):
        parser = PydanticOutputParser(pydantic_object=pydantic_object)
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["examples"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        examplesStr = ""

        for example in examples:
            examplesStr += example.model_dump_json() + "\n---\n"

        returnVals = []
        MAX_RETRIES = 3

        retries = 0
        current_count = 0
        while current_count < count:
            try:
                current_count += 1

                chain = prompt | model | parser
                response = chain.invoke({"examples": examplesStr})
                returnVals.append(response)

                print(response.model_dump_json(indent=2))

                retries = 0

            except Exception as e:

                if retries >= MAX_RETRIES:
                    print(f"Failed to generate example after {retries} retries")
                    retries = 0
                    continue

                current_count -= 1
                retries += 1
                print(e)

        return returnVals




# def generate_llm_output():
#     try:
#         parser = PydanticOutputParser(pydantic_object=ChroniclerTrainingEntry)
#         prompt = PromptTemplate(
#             template=INITIAL_SCENE_PROMPT_TEMPLATE,
#             input_variables=["examples"],
#             partial_variables={"format_instructions": parser.get_format_instructions()},
#         )

#         examplesStr = ""

#         for example in initial_scene_examples:
#             examplesStr += example.model_dump_json() + "\n---\n"

#         chain = prompt | model | parser
#         response  = chain.invoke({"examples": examplesStr})

#         entry = response
#         print(entry.model_dump_json(indent=2))
#         return entry

#     except Exception as e:
#         print(e)
#         return []


# generate_llm_output()
