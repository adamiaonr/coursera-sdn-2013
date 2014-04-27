from datetime import date
from datetime import datetime
from decimal import Decimal
from time import mktime
import decimal
import time
import sys
import os
import collections
import math

def main():

    layers = {1:'core', 2:'aggregation', 3:'edge', 4:'host'}

    print layers

    for layer, n in sorted(layers.iteritems()):
        print layer, n

        if n != 'host':
            print "the wrong stuff"
        else:
            print "the right stuff"

        i = 4
        d = "{var1}{var2}".format(var1 = n[0],var2 = i)

        print layers[1]

        print d
        print math.ceil(3.1)

if __name__ == "__main__":
    main()
