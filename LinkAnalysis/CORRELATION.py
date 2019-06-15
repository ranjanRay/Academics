
import numpy as np

def correlation(old, new) :

    list1 = []
    list2 = []

    for eachKey in old.keys() :

        list1.append(old[eachKey])
        list2.append(new[str(eachKey)])

    return np.corrcoef(list1, list2) [0, 1]
