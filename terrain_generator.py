import random
import string
import os
import functools


# noinspection PyPep8Naming
def get_random_CHN_symbol():
    symbols_probability = {'C': 10, 'H': 5, 'N': 10}
    _sum = functools.reduce(lambda l, r: l+r, symbols_probability.values())
    random_int = random.randint(1, _sum)
    current_num = 0
    for key, value in symbols_probability.items():
        current_num += value
        if current_num >= random_int:
            return key


def generate_random_terrain(width=5, height=5, num_of_princesses=3):
    _terrain = ['' for i in range(height)]
    for y in range(height):
        for x in range(width):
            _terrain[y] += get_random_CHN_symbol()

    dragon_coords = (random.randint(0, width-1), random.randint(0, height-1))
    princesses_coords = []
    for princess_num in range(num_of_princesses):
        princess_coords = (random.randint(0, width-1), random.randint(0, height-1))
        while princess_coords in princesses_coords or princess_coords == dragon_coords:
            princess_coords = (random.randint(0, width-1), random.randint(0, height-1))
        princesses_coords.append(princess_coords)

    new_line = list(_terrain[dragon_coords[1]])
    new_line[dragon_coords[0]] = 'D'
    _terrain[dragon_coords[1]] = ''.join(new_line)

    for princess in princesses_coords:
        new_line = list(_terrain[princess[1]])
        new_line[princess[0]] = 'P'
        _terrain[princess[1]] = ''.join(new_line)

    return _terrain

file = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(3)) + '.txt'
path = os.path.join('generated', file)

terrain = generate_random_terrain(20, 20)

print('Written into ' + file)

with open(path, 'w') as f:
    for line in terrain:
        f.write(line + '\n')
