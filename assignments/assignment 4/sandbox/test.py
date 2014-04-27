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

    my_list = {1,2,3,4}
    my_string = 4

    result = [is_equal(my_string,item) for item in my_list]

    print result

def is_equal(x,y):

    if x == y:
        return "OK"
    else:
        return "NOT OK"

if __name__ == "__main__":
    main()
