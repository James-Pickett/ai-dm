from synthetic_data_gen import ChroniclerTrainingEntry, ChroniclerInput, ChroniclerOutput, SceneNotes, Generator

INITIAL_SCENE_PROMPT_TEMPLATE = """
You are an AI assistant designed to generate realistic training data for a table top role-playing game (TTRPG) campaign.
This training data will be used to train an AI assistant known as the Chronicler, which helps the dungeon master keep track of their campaigns.
Your task is to generate examples for the Chronicler to learn from.

The current focus is on the opening scene of an adventure.

You will generate:
1. A **player utterance** where the player provides a character name.
2. A **dungeon master utterance** that uses specific, capitalized proper names for all characters, locations, and items.
   - **Important:** When describing any location, always include a specific, proper name. For example, instead of "a small tavern in the city," use "The Silver Chalice in Havenbrook." Avoid generic terms like "forest," "temple," or "city."

Then, generate **scene notes** based on these utterances.

########
Instructions:
- The player utterance should include a named character.
- The dungeon master utterance must use specific names for all locations and items.
- Do not infer or add details beyond what is provided in the utterances.

########
Examples:
{examples}

########
Return only a JSON object in this format:
{format_instructions}

########
Now, generate an example dungeon master utterance and create new scene notes based on the player and dungeon master utterances.
"""

initial_scene_examples = [
    ChroniclerTrainingEntry(
        chronicler_input=ChroniclerInput(
            player_utterance="My player's name is Creb. Lets have a viking themed adventure.",
            game_master_utterance="""You are Creb, a grizzled veteran of the Dreadwood Wars with a scarred face and battle-hardened frame. Years of surviving the bloodshed have left you with a keen instinct for danger and a sharp wit, though your haunted eyes reveal the dark memories that plague you.

You find yourself in the taproom of the Silver Chalice, a rough-and-tumble establishment nestled in the heart of Havenbrook. The air is thick with smoke and the smell of spilled ale, while the sounds of raucous laughter and clinking tankards fill the space. A weathered barkeep named Old Tom stands behind the counter, methodically wiping down mugs as he keeps an eye on the rowdy crowd. The room buzzes with gossip about recent raids from the Dreadwood and whispers of a growing cult activity in the outskirts of town.""",
        ),
        chronicler_output=ChroniclerOutput(
            scene_notes=SceneNotes(
                player_characters=["Creb"],
                non_player_characters=["Old Tom"],
                players_characters_location=["Havenbrook", "the Silver Chalice"],
                scene_details=[
                    "The air is thick with smoke and the smell of spilled ale",
                    "The sounds of raucous laughter and clinking tankards fill the space",
                    "Old Tom stands behind the counter, methodically wiping down mugs as he keeps an eye on the rowdy crowd"
                    "The room buzzes with gossip about recent raids from the Dreadwood and whispers of a growing cult activity in the outskirts of town",
                ]
            ),
            campaign_facts=[
                "Creb is a player character with a scarred face, battle-hardened frame, and haunted eyes",
                "Creb is a grizzled veteran of the Dreadwood Wars",
                "Old Tom is the weathered barkeep of the Silver Chalice",
                "The Silver Chalice is a rough-and-tumble establishment in the heart of Havenbrook",
            ]
        ),
    ),
    ChroniclerTrainingEntry(
        chronicler_input=ChroniclerInput(
            player_utterance="My characters name is Cassie, a wood elf ranger, let start an adventure is a small wood elf village in the forrest.",
            game_master_utterance="""The morning sun filters through the canopy of ancient trees, dappling the forest floor with shifting patterns of light. In a small clearing surrounded by massive oaks and maples, the village of Brambletown nestles amidst the undergrowth. Wooden walkways connect rustic homes built into the trees, while moss-covered stone paths weave between them.

Cassie, a lithe wood elf ranger with copper skin and dark hair, descends a narrow trail leading from her elevated home. Her green eyes take in the familiar surroundings - the sweet scent of wildflowers mixes with woodsmoke from cooking fires. Other elves move purposefully about their daily tasks, some greeting Cassie with warm smiles while others remain absorbed in their work.

The village center holds the Heart Tree, its massive trunk reaching skyward, where village elders gather to discuss matters. Nearby, children play in a cleared area while their parents work nearby, crafting bows and arrows or weaving baskets from supple branches. The village's quiet harmony is broken only by the calls of birds and the rustling of leaves.""",
        ),
        chronicler_output=ChroniclerOutput(
            scene_notes=SceneNotes(
                player_characters=["Cassie"],
                non_player_characters=[],
                players_characters_location=["Brambletown"],
                scene_details=[
                    "The morning sun filters through the canopy of ancient trees, dappling the forest floor with shifting patterns of light",
                    "Nearby, children play in a cleared area while their parents work nearby, crafting bows and arrows or weaving baskets from supple branches",
                    "The village's quiet harmony is broken only by the calls of birds and the rustling of leaves",
                    "The sweet scent of wildflowers mixes with woodsmoke from cooking fires",
                    "Elves move purposefully about their daily tasks, some greeting Cassie with warm smiles while others remain absorbed in their work"
                ]
            ),
            campaign_facts=[
                "Cassie is a wood elf ranger with copper skin and dark hair",
                "Brambletown is a village is in a small clearing, surrouned by massive oaks and maples in the forest, with wooden walkways connecting rustic homes built into the trees, moss-covered stone paths weaving between them",
                "The Heart Tree is a massive trunk in Brambletown reaching skyward where village elders gather to discuss matters",
            ]
        ),
    ),
    ChroniclerTrainingEntry(
        chronicler_input=ChroniclerInput(
            player_utterance="Hi, I'm Raleigh Royal, my nick name is Albatross. Lets start a pirate themed adventure!",
            game_master_utterance="""The year is 1714 and you are the notorious pirate captain, Raleigh Royal, better known by your nickname "Albatross." Your reputation for ruthless efficiency and keen wit has earned you a place among the most feared names in the Caribbean.

You stand at the helm of the Swift Serpent, a sleek frigate flying your Jolly Roger, as it cuts through the azure waters off the coast of Tortuga. The salty spray splashes against your weathered face while your crew of hardened cutthroats performs their duties with practiced efficiency. On the horizon, you spot the distinctive sails of a merchant vessel, its cargo holds likely brimming with Spanish gold destined for the New World. The wind is at your back, and the promise of plunder fills the air.

Your First Mate, the weathered Irishman James "BlackJack" Sullivan, stands ready at your side, his scarred face twisted into a predatory grin as he watches the merchant ship draw closer. The rest of your crew bustles about their stations, checking weapons and preparing for what promises to be an exciting afternoon. The merchant vessel's captain has spotted you and is frantically trying to change course, but your superior speed and the wind at your back will allow you to intercept him within minutes.""",
        ),
        chronicler_output=ChroniclerOutput(
            scene_notes=SceneNotes(
                player_characters=["Raleigh \"Albatross\" Royal"],
                non_player_characters=["James \"BlackJack\" Sullivan"],
                players_characters_location=["the Carribbean", "off the coast of Tortuga", "on board the Swift Serpent"],
                scene_details=[
                    "The salty spray splashes against your weathered face",
                    "You stand at the helm of the Swift Serpent, a sleek frigate flying your Jolly Roger, as it cuts through the azure waters off the coast of Tortuga"
                    "Your crew of hardened cutthroats performs their duties with practiced efficiency",
                    "The wind is at your back, and the promise of plunder fills the air",
                    "James \"BlackJack\" Sullivan stands ready at your side, his scarred face twisted into a predatory grin as he watches the merchant ship draw closer",
                    "The rest of your crew bustles about their stations, checking weapons and preparing for what promises to be an exciting afternoon",
                    "The merchant vessel's captain has spotted you and is frantically trying to change course, but your superior speed and the wind at your back will allow you to intercept him within minutes",
                ]
            ),
            campaign_facts=[
                "Raleigh \"Albatross\" Royal is a notorious pirate captain with a reputation for ruthless efficiency and keen wit",
                "Raleigh \"Albatross\" Royal commands the Swift Serpent",
                "James \"BlackJack\" Sullivan is a weathered Irishman and the First Mate of Raleigh \"Albatross\" Royal",
                "The Swift Serpent is a sleek frigate, a sleek frigate flying the Jolly Roger",
            ]
        ),
    ),
]

Generator().generate(INITIAL_SCENE_PROMPT_TEMPLATE, ChroniclerTrainingEntry, initial_scene_examples, count=5)
