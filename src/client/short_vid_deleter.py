'''
Run this file to clear up any videos under 12MB in size. This should be the equivalent of around 5 seconds
'''

import os, sys

min_byte_size = 12_000_000

while True:
    for mouse_num in range(1, 6):
        for f in os.listdir('../../AnimalProfiles/MOUSE' + str(mouse_num) + '/Videos/'):
            if "temp" not in f and "tmp" not in f:
                if os.path.getsize('../../AnimalProfiles/MOUSE' + str(mouse_num) + '/Videos/' + f) < min_byte_size:
                    os.remove('../../AnimalProfiles/MOUSE' + str(mouse_num) + '/Videos/' + f)