import random
import math
import json

MAP_STYLES = [
    "BASIC",
    "BIG_ISLANDS",
    "CENTER_LAKE",
    "DROP_PLATEAU",
    "FLOODED",
    "HIGH_RECLAIM",
    "LAND_BRIDGE",
    "LITTLE_MOUNTAIN",
    "LOW_MEX",
    "MOUNTAIN_RANGE",
    "MULTILEVEL",
    "ONE_ISLAND",
    "SMALL_ISLANDS",
    "VALLEY",
    "RIVERS",
    "RIVERS_AND_OCEANS",
    "FRACTAL_LAND",
    "FRACTAL_PLATEAU",
    "FRACTAL_NAVY",
    "SETONISH",
    # "FORREST_SOMETHING",
]

TERRAIN_SYMMETRIES = [
    "POINT2",
    #"POINT3",
    "POINT4",
    #"POINT5",
    "POINT6",
    #"POINT7",
    "POINT8",
    #"POINT9",
    "POINT10",
    #"POINT11",
    "POINT12",
    #"POINT13",
    "POINT14",
    #"POINT15",
    "POINT16",
    "XZ",
    "ZX",
    "X",
    "Z",
    "QUAD",
    "DIAG",
    "NONE",
]

TEXTURE_STYLES = [
    "BRIMSTONE",
    "DESERT",
    "EARLYAUTUMN",
    "FRITHEN",
    "MARS",
    "MOONLIGHT",
    "PRAYER",
    "STONES",
    "SUNSET",
    "SYRTIS",
    "WINDINGRIVER",
    "WONDER",
    "CRYSTALLINE",
]

TERRAIN_STYLES = [
    "BASIC",
    "BASIC_LAST",
    "BIG_ISLANDS",
    "CENTER_LAKE",
    "CENTER_LAKE_LAST",
    "DROP_PLATEAU",
    "DROP_PLATEAU_LAST",
    "FLOODED",
    "LAND_BRIDGE",
    "LITTLE_MOUNTAIN",
    "LITTLE_MOUNTAIN_LAST",
    "MOUNTAIN_RANGE",
    "MOUNTAIN_RANGE_LAST",
    "MULTILEVEL_LAST",
    "ONE_ISLAND",
    "SMALL_ISLANDS",
    "VALLEY",
    "VALLEY_LAST",
    "RIVERS",
    "RIVERS_AND_OCEANS",
    "FRACTAL_LAND",
    "FRACTAL_PLATEAU",
    "FRACTAL_NAVY",
    "SETONS",
]

RESOURCE_STYLES = [
    "BASIC",
    "LOW_MEX",
    "WATER_MEX",
    "HI_MEX_LAND_LOW_MEX_WATER",
    #"ONE_HYDRO_NO_MEX",
]

PROP_STYLES = [
    "BASIC",
    "BOULDER_FIELD",
    "ENEMY_CIV",
    "HIGH_RECLAIM",
    "LARGE_BATTLE",
    "NAVY_WRECKS",
    "NEUTRAL_CIV",
    "ROCK_FIELD",
    "SMALL_BATTLE",
    "FORREST_SOMETHING",
]



def convert_to_grid_units(value):

    value = float(value)
    if value < 512:
        value = value * 512 / 10

    return int(value)

def generate_map_config(options):
    """
    Generate a randomized map configuration.

    Any parameter set to None will be randomly generated.
    """
    
    config = {
        # Mapsize in km, max 20km
        "map_size": options.get("map_size", f"{random.randint(5, 20)}km"),
    
        # Max 16 spawns
        "spawn_count": options.get("spawn_count", random.randint(2, 16)),
    
        # Default/random teams = 2
        "num_teams": options.get("num_teams", 2),
    
        "style": options.get("style", random.choice(MAP_STYLES)),

    
    }

    if not options.get("style"):

        config["terrain_symmetry"] = options.get(
            "terrain_symmetry",
            random.choice(TERRAIN_SYMMETRIES),
        )
    
        config["texture_style"] = options.get(
            "texture_style",
            random.choice(TEXTURE_STYLES),
        )
    
        config["terrain_style"] = options.get(
            "terrain_style",
            random.choice(TERRAIN_STYLES),
        )
    
        config["resource_style"] = options.get(
            "resource_style",
            random.choice(RESOURCE_STYLES),
        )
    
        config["prop_style"] = options.get(
            "prop_style",
            random.choice(PROP_STYLES),
        )

        # Float between 0 and 1
        config["reclaim_density"] = options.get(
            "reclaim_density",
            round(random.uniform(0, 1), 2),
        )
    
        # Float between 0 and 1
        config["resource_density"] = options.get(
            "resource_density",
            round(random.uniform(0, 1), 2),
        )

    # normalize mapsize
    config["map_size"] = convert_to_grid_units(config["map_size"])

    # fix overlapping style config #
    if any([x in config for x in ["texture_style", "terrain-style", "resource-style", "prop-style"]]):
        del config["style"]
    
    import json
    print(json.dumps(config, indent=2))
    return config


if __name__ == "__main__":
    config = generate_map_config()
    print(config)
