import numpy as np
import json

#make_directions_familes
direction_families = []
for i in range(8):
    for j in range(8):
        for k in range(8):
            if i + j + k < 10:
                if ([i/2, j/2, k/2] not in direction_families and
                    [i/3, j/3, k/3] not in direction_families and
                    [i/4, j/4, k/4] not in direction_families and
                    [i/5, j/5, k/5] not in direction_families and
                    [i/6, j/6, k/6] not in direction_families and
                    [i/7, j/7, k/7] not in direction_families and
                    [i/8, j/8, k/8] not in direction_families):

                        direction_families.append([i,j,k])

dictionary = {}

# use this for after reading the json
##for i,j,k in direction_families.copy():
##    for u in (-1, 1):
##        for v in (-1, 1):
##            for w in (-1, 1):
##                 pass
##                #put all negatives in

for i,j,k in direction_families:
    name = ''.join((str(i),str(j),str(k)))
    if i + j + k == 1:
        color = (239,154,154)
        ms = 100
        marker = 's'
    elif i + j + k == 2:
        color = (144,202,249)
        ms = 100
        marker = 'D'
    elif i == 1 and j == 1 and k == 1:
        color = (165,214,167)
        ms = 100
        marker = '^'
    elif i*j*k == 2:
        color = (206,147,216)
        ms = 50
        marker = 'o'
    else:
        color = (189,189,189)
        ms = 50 - (i+j+k) * 5
        marker = 'o'
        
    dictionary[name] = {'color':color,
                        'ms':ms,
                        'marker':marker}


whole_dic = {}
whole_dic['Current'] = 'Default'
whole_dic['Default'] = dictionary


with open('data/markers.json', 'w') as fp:
    json.dump(whole_dic, fp, sort_keys=True, indent=4)

#with open('data.json', 'r') as fp:
#    data = json.load(fp)
