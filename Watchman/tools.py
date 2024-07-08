import Levenshtein
import traceback
import io


def diff_lists(oldlist, newlist):
    return list(set(newlist) - set(oldlist))


def memory_diff_files(oldfilename, newfilename):
    try:
        old = open(oldfilename, 'r').read().split()
        new = open(newfilename, 'r').read().split()
        return diff_lists(old, new)
    except IOError:
        traceback.print_exc()


def diff_files(old_file, new_file):
    new_list = []

    old = old_file.readline().strip()
    new = new_file.readline().strip()

    while len(old) > 0:
        if old == new:
            old = old_file.readline().strip()
            new = new_file.readline().strip()
        elif new < old:
            new_list.append(new)
            new = new_file.readline().strip()
        else:
            old = old_file.readline().strip()

    new_list.append(new)
    for line in new_file:
        new_list.append(line.strip())

    return new_list
