def GetSymbs():
    with open('symbs_list.txt', 'r') as filehandle:
            return [symb.rstrip() for symb in filehandle.readlines()]