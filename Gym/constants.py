# Imports:
import json

# Opening the settings file:
with open('settings.json', 'r') as settings_file:
    
    # Reading the data:
    data = json.load(settings_file)


# Agent settings:
INITIAL_ENERGY = data["agent_settings"]["initial_energy"]
INITIAL_SPEED = data["agent_settings"]["initial_speed"]

# Gym settings:
GENERATION_COUNT = data["gym_settings"]["generation_count"]
FOOD_COUNT = data["gym_settings"]["food_count"]
SCREEN_FPS = data["gym_settings"]["screen_fps"]
FOOD_ENERGY = data["gym_settings"]["food_energy"]
FOOD_FITNESS = data["gym_settings"]["food_fitness"]
AGENT_ANGLE_CHANGE = data["gym_settings"]["agent_angle_change"]