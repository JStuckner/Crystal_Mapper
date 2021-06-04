def cubic_family_of_directions():
    out = {}
    direction_families = ['100', '110', '111', '221', '321']
    direction_families = ['100', '110', '111']
    for family in direction_families:
        out[family] = []
        for u in [int(family[0]), -int(family[0])]:
            for v in [int(family[1]), -int(family[1])]:
                for w in [int(family[2]), -int(family[2])]:
                    directions = [[u,v,w], [u,w,v],
                                  [v,u,w], [v,w,u],
                                  [w,u,v], [w,v,u]]
                    for dir in directions:
                        if dir not in out[family]:
                            out[family].append(dir)
    return out

def tetragonal_family_of_directions():
    out = {}
    direction_families = ['100', '001', '110', '111', '221', '321']
    for family in direction_families:
        out[family] = []
        for u in [int(family[0]), -int(family[0])]:
            for v in [int(family[1]), -int(family[1])]:
                for w in [int(family[2]), -int(family[2])]:
                    directions = [[u,v,w], [v,u,w]]
                    for dir in directions:
                        if dir not in out[family]:
                            out[family].append(dir)
    return out


if __name__ == '__main__':
    a = tetragonal_family_of_directions()
    print(a['100'])
    print(a['001'])