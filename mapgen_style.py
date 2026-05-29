import random
import math


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
    "FORREST_SOMETHING",
]

TERRAIN_SYMMETRIES = [
    "POINT2",
    "POINT3",
    "POINT4",
    "POINT5",
    "POINT6",
    "POINT7",
    "POINT8",
    "POINT9",
    "POINT10",
    "POINT11",
    "POINT12",
    "POINT13",
    "POINT14",
    "POINT15",
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
    "ONE_HYDRO_NO_MEX",
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



def round_up_to_5(km):
    return str(math.ceil(int(km.strip("km")) / 5) * 5) + "km"

def generate_map_config(
    _=None,
    map_size=None,
    spawn_count=None,
    num_teams=None,
    style=None,
    terrain_symmetry=None,
    texture_style=None,
    terrain_style=None,
    resource_style=None,
    prop_style=None,
    reclaim_density=None,
    resource_density=None,
    **kwargs,
):
    """
    Generate a randomized map configuration.

    Any parameter set to None will be randomly generated.
    """

    config = {
        # Mapsize in km, max 20km
        "map_size": map_size if map_size is not None else f"{random.randint(5, 20)}km",

        # Max 16 spawns
        "spawn_count": spawn_count if spawn_count is not None else random.randint(2, 16),

        # Default/random teams = 2
        "num_teams": num_teams if num_teams is not None else 2,

        "style": style if style is not None else random.choice(MAP_STYLES),

        "terrain_symmetry": (
            terrain_symmetry
            if terrain_symmetry is not None
            else random.choice(TERRAIN_SYMMETRIES)
        ),

        "texture_style": (
            texture_style
            if texture_style is not None
            else random.choice(TEXTURE_STYLES)
        ),

        "terrain_style": (
            terrain_style
            if terrain_style is not None
            else random.choice(TERRAIN_STYLES)
        ),

        "resource_style": (
            resource_style
            if resource_style is not None
            else random.choice(RESOURCE_STYLES)
        ),

        "prop_style": (
            prop_style
            if prop_style is not None
            else random.choice(PROP_STYLES)
        ),

        # Float between 0 and 1
        "reclaim_density": (
            reclaim_density
            if reclaim_density is not None
            else round(random.uniform(0, 1), 2)
        ),

        # Float between 0 and 1
        "resource_density": (
            resource_density
            if resource_density is not None
            else round(random.uniform(0, 1), 2)
        ),
    
    }

    # normalize mapsize
    config["map_size"] = round_up_to_5(config["map_size"])

    # fix overlapping style config #
    if any([x in config for x in ["texture_style", "terrain-style", "resource-style", "prop-style"]]):
        del config["style"]
    
    import json
    print(json.dumps(config, indent=2))
    return config


if __name__ == "__main__":
    config = generate_map_config()
    print(config)
