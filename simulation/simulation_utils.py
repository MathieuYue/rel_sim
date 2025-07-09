def print_separator():
    print("------------------------------------------------------------------------------")

def print_formatted(source, output_str):
    if source == 0:
        color = '\033[91m'
    elif source == 1:
        color = '\033[92m'
    else:
        color = '\033[94m'
    print(f'{color}{output_str}\033[0m')

def print_scene_separator(scene_ind):
    print(f'-------------------------------- SCENE {scene_ind} --------------------------------')