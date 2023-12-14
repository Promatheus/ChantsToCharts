import numpy


def elojel_ertek(ertek):
    # return numpy.sign(ertek)
    ertek1 = ertek / (abs(ertek) + 1)
    ertek2 = -1 * ertek / (abs(-1 * ertek) + 1)
    print(ertek1, ertek2)
    return int(ertek1 - ertek2)