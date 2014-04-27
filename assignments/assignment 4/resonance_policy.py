'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 7 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Muhammad Shahbaz
'''

################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.examples.load_balancer import *

class ResonancePolicy():

  state_policy_map = {}

  def __init__(self):
    self.state_policy_map['default'] = self.default_policy

  def get_policy(self, state):
    if self.state_policy_map.has_key(state):
      return self.state_policy_map[state]
    else:
      return self.default_policy
    
  """ Default state policy """
  def default_policy(self):
    return drop

class LBPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def portA_policy(self):                       

    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1')]
    repeating_R =  [IP('10.0.0.2')]
    # This will replace the incoming packet[src=10.0.0.1, dst=10.0.0.100] to packet[src=10.0.0.1, dst=10.0.0.2] and
    #                            and packet[src=10.0.0.1, dst=10.0.0.2] back to packet[src=10.0.0.1, dst=10.0.0.100]
    return rewrite(zip(client_ips, repeating_R), public_ip)
    
  def portB_policy(self):

    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1')]
    repeating_R =  [IP('10.0.0.3')]
    # This will replace the incoming packet[src=10.0.0.1, dst=10.0.0.100] to packet[src=10.0.0.1, dst=10.0.0.3] and
    #                            and packet[src=10.0.0.1, dst=10.0.0.3] back to packet[src=10.0.0.1, dst=10.0.0.100]
    return rewrite(zip(client_ips, repeating_R), public_ip)

# --------- Update the code below ------------

  def default_policy(self):

    host_list = self.fsm.get_portA_hosts()

    # check a 'cooler' way to do the same below...
#    matches = none
#    for host in host_list:
#        matches = matches + match(srcip=IP(host)) + match(dstip=IP(host))

#    return if_(matches, self.portA_policy(), self.portB_policy())

    # [match(srcip=IP(host)) for host in host_list] performs a series of 
    # match() operations, for each 'host' item in host_list. we use 
    # parallel() to achieve the same behaviour as matches += (...)
    return if_(parallel([match(srcip=IP(host)) for host in host_list]) + parallel([match(dstip=IP(host)) for host in host_list]), self.portA_policy(), self.portB_policy())

