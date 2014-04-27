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

    firewall = {}

    policyFilePath = "%s/Dropbox/Workbench/SDN/assignments/assignment 2/firewall-policies.csv" % os.environ[ 'HOME' ]

    policyFile = open(policyFilePath)
    policyLines = policyFile.readlines()

    for policyLine in policyLines:

        # skip the header line
        if not is_number(policyLine.split(',')[0]):
            continue

        print policyLine

        firewall[(policyLine.split(',')[1],
                policyLine.replace("\n","").split(',')[2])] = "blrgh..."

    print "2nd part of testing..."

    for entry in firewall:
        print entry[0]
        print firewall[entry]

def is_number(s):

    try:
        float(s)
        return True

    except ValueError:
        return False

if __name__ == "__main__":
    main()
