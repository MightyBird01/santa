

read file, create pathes
add one to filename!
calc metric


def perm (path, lenPerm):
    positions = range(0,len(path)-lenPerm+1)
    print (positions)
    result = []
    for i in positions:
        first = path[0:i]
        middle = path[i:i+lenPerm]
        last = path[i+lenPerm:len(path)]
        #print (first, middle, last)
        perms = list(itertools.permutations(middle, lenPerm))
        for p in perms:
            l = first + list(p) + last
            result.append(l)
    return (result)


tot = [1,2,3,4,5,6,7,8,9,10]
r = perm(tot,5)
print (len(r))
print (r)


try to improve until keystroke or num iter or all pathes improved...


calc metric
change name of file!
save file

