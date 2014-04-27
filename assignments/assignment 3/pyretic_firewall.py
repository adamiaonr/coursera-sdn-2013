'''
    Coursera:
    - Software Defined Networking (SDN) course
    -- Module 6 Programming Assignment
    
    Professor: Nick Feamster
    Teaching Assistant: Muhammad Shahbaz
'''

################################################################################
# The Pyretic Project                                                          #
# frenetic-lang.org/pyretic                                                    #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
################################################################################
# Licensed to the Pyretic Project by one or more contributors. See the         #
# NOTICES file distributed with this work for additional information           #
# regarding copyright and ownership. The Pyretic Project licenses this         #
# file to you under the following license.                                     #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided the following conditions are met:       #
# - Redistributions of source code must retain the above copyright             #
#   notice, this list of conditions and the following disclaimer.              #
# - Redistributions in binary form must reproduce the above copyright          #
#   notice, this list of conditions and the following disclaimer in            #
#   the documentation or other materials provided with the distribution.       #
# - The names of the copyright holds and contributors may not be used to       #
#   endorse or promote products derived from this work without specific        #
#   prior written permission.                                                  #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     #
# LICENSE file distributed with this work for specific language governing      #
# permissions and limitations under the License.                               #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

import os

# insert the name of the module and policy you want to import
from pyretic.examples.pyretic_switch import act_like_switch

policyFilePath = "%s/pyretic/pyretic/examples/firewall-policies.csv" % os.environ[ 'HOME' ]  
#policyFilePath = "%s/Dropbox/Workbench/SDN/assignments/assignment 3/firewall-policies.csv" % os.environ[ 'HOME' ]

# Translation of firewall actions into Boolean values, as 
# used in our implementation: 0x00 is for DROP actions, 0x01 is for 
# FORWARD actions. These are helpful for better code readability.
DROP    = 0x00
FORWARD = 0x01
UNKNOWN = 0x02

@dynamic
def act_like_firewall(self):

    # start with a policy that doesn't match any packets
    self.not_allowed = none

    # Firewall (MAC pair version) rule table.
    self.firewall_policy_table = {}

    # Fill the firewall table with the contents from policyFile.
    policyFile = open(policyFilePath)
    policyLines = policyFile.readlines()
    policyFile.close()

    def is_number(s):
        '''
        Checks if s is a number or not.
        '''
        try:
            float(s)
            return True
        except ValueError:
            return False

    for policyLine in policyLines:

        # Skip the header line.
        if not is_number(policyLine.split(',')[0]):
            continue

        # For now, we are just interested in DROPing packets that match 
        # the (mac_a, mac_b) pairs in policyFile.
        entry = DROP

        mac_a = MAC(policyLine.split(',')[1])
        mac_b = MAC(policyLine.replace("\n","").split(',')[2])

        # Don't forget to use EthAddr() to turn the MAC address strings 
        # into proper structures for comparison with the PacketIn event 
        # attributes.
        self.firewall_policy_table[(mac_a, mac_b)] = entry

    # and add traffic that isn't allowed
    for policy in self.firewall_policy_table:
        self.not_allowed = self.not_allowed + match(srcmac=policy[0], dstmac=policy[1]) + match(srcmac=policy[1], dstmac=policy[0])

    # express allowed traffic in terms of not_allowed - hint use '~'
    self.allowed = ~self.not_allowed

    # update the policy
    self.policy = (self.allowed >> act_like_switch())

    print self.policy

def main():
    return act_like_firewall()

