'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 4 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Muhammad Shahbaz
'''

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
from collections import namedtuple
import os

log = core.getLogger()
policyFilePath = "%s/pox/pox/misc/firewall-policies.csv" % os.environ[ 'HOME' ]  
#policyFilePath = "%s/Dropbox/Workbench/SDN/assignments/assignment 2/firewall-policies.csv" % os.environ[ 'HOME' ]

''' Add your global variables here ... '''

# Translation of firewall actions into Boolean values, as 
# used in our implementation: 0x00 is for DROP actions, 0x01 is for 
# FORWARD actions. These are helpful for better code readability.
DROP    = 0x00
FORWARD = 0x01
UNKNOWN = 0x02

# Default timeout values (taken from l2_learning.py code examples).
DEFAULT_IDLE_TIMEOUT = 60
DEFAULT_HARD_TIMEOUT = 300

# Default listener priority for the firewall application.
DEFAULT_FIREWALL_PRIORITY = 50

class Firewall (EventMixin):

    def __init__ (self, connection):

        log.debug("Firewall::init(): Initializing Firewall module.")

        # I'm not sure about this, just following similarities in the 
        # l2_learning.py project.
        self.connection = connection

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
            # the (src_mac, dst_mac) pairs in policyFile.
            entry = DROP

            src_mac = EthAddr(policyLine.split(',')[1])
            dst_mac = EthAddr(policyLine.replace("\n","").split(',')[2])

            # Don't forget to use EthAddr() to turn the MAC address strings 
            # into proper structures for comparison with the PacketIn event 
            # attributes.
            self.firewall_policy_table[(src_mac, dst_mac)] = entry

            log.debug("Firewall::init(): Added policy (%s,%s,%s) to firewall policy table.", 
                src_mac, dst_mac, 
                ("FORWARD" if (entry == FORWARD) else "DROP"))

            self.InstallPolicy(src_mac, dst_mac, entry)
            # TODO: Just realized the traffic should be blocked in a 
            # bi-directional fashion.
            self.InstallPolicy(dst_mac, src_mac, entry)

        # We want to hear PacketIn messages, so we listen
        # to the connection
        connection.addListeners(self, priority=DEFAULT_FIREWALL_PRIORITY)

    def _handle_PacketIn (self, event):

        # Parse the packet event.
        packet = event.parsed

        # Check if packet's dl_src, dl_dst pair matches any pair in our 
        # firewall table.
        # If there's a match on the firewall table with an associated DROP 
        # action, drop the packet and add an appropriate flow 
        # table entry.
        if self.CheckPolicy(packet.src, packet.dst) == DROP:

            # Create the flow table entry to install at the switch which has 
            # just connected with this POX controller. The flow table entry 
            # shall specify an ofp_match object with the appropriate 
            # (src_mac, dst_mac) 
            # tuple and an ofp_action_output action object set to DROP the 
            # packet. According to 
            # http://pages.cs.wisc.edu/~agember/sdn/code/LearningSwitch.txt, a 
            # DROP action is modeled by the absence of actions on the 
            # ofp_flow_mod entry. This is consistent with the explanation 
            # given by Nick Feamster in video lecture 4.1 ("The Control Plane") 
            # for an OpenFlow Drop action: 'A flow entry with NO SPECIFIED 
            # ACTION indicates that all matching packets should be dropped.'

            # Halt the event, so that no further handlers handle the PacketIn 
            # event (this is related to the conflicting rule issue in the 
            # assignment).
            #event.halt = True

            self.InstallPolicy(packet.src, packet.dst)

            return EventHalt

    def CheckPolicy (self, packet_src_mac, packet_dst_mac):
        '''
        Checks if the packet's (src_mac, dst_mac) tuple is present on the 
        firewall policy table. Returns the associated action (FORWARD or DROP).
        '''

        log.debug("Firewall::CheckPolicy(): Checking tuple (%s,%s).", 
            packet_src_mac, packet_dst_mac)

        print self.firewall_policy_table

        try:
            entry = self.firewall_policy_table[(packet_src_mac, packet_dst_mac)]

            log.debug("Policy (%s,%s) found on firewall policy table. Action is %s.", 
                packet_src_mac, packet_dst_mac, 
                ("FORWARD" if (entry == FORWARD) else "DROP"))

            return entry

        except KeyError:
            log.debug("Policy (%s,%s) not found on firewall policy table.", 
                packet_src_mac, packet_dst_mac)

            return UNKNOWN

    def AddPolicy (self, packet_src_mac, packet_dst_mac, value=DROP):
        '''
        Adds a new policy to the firewall_policy_table (if it doesn't exist 
        yet).
        '''

        # Check if value is valid (by valid we mean DROP or FORWARD).
        if ((value & ~(DROP | FORWARD)) != 0x00):
            log.debug("Invalid policy to add (%s,%s,%s). Aborting.", 
                packet_src_mac, packet_dst_mac, value)

            return False

        if CheckPolicy(packet_src_mac, packet_dst_mac) == UNKNOWN:

            self.firewall_policy_table[(packet_src_mac, packet_dst_mac)] = value
            log.debug("Added policy (%s,%s,%s) to firewall policy table.", 
                packet_src_mac, packet_dst_mac, 
                ("FORWARD" if (value == FORWARD) else "DROP"))

            return True

        return False

    def InstallPolicy (self, packet_src_mac, packet_dst_mac, value=DROP):
        '''
        Install a new flow table entry to the switch, relative to a 
        firewall_policy_table entry.
        '''

        # Check if value is valid (by valid we mean DROP or FORWARD).
        if ((value & ~(DROP | FORWARD)) != 0x00):
            log.debug("Firewall::UploadPolicy(): Invalid policy to add (%s,%s,%s). Aborting.", 
                packet_src_mac, packet_dst_mac, value)

            return False

        # Create the flow table entry to install at the switch which has 
        # just connected with this POX controller. The flow table entry 
        # shall specify an ofp_match object with the appropriate 
        # (src_mac, dst_mac) 
        # tuple and an ofp_action_output action object set to DROP the 
        # packet. According to 
        # http://pages.cs.wisc.edu/~agember/sdn/code/LearningSwitch.txt, a 
        # DROP action is modeled by the absence of actions on the 
        # ofp_flow_mod entry. This is consistent with the explanation 
        # given by Nick Feamster in video lecture 4.1 ("The Control Plane") 
        # for an OpenFlow Drop action: 'A flow entry with NO SPECIFIED 
        # ACTION indicates that all matching packets should be dropped.'

        # Note that the OpenFlow message we're interested in here is 
        # ofp_flow_mod (and not ofp_packet_out) as we want to instruct 
        # the switch to install a flow table entry (and not to send 
        # a packet).
        msg = of.ofp_flow_mod()

        # The ofp_match object fields of interest here are the src and dst 
        # MAC addresses of the layer 2 frame.
        msg.match = of.ofp_match()
        msg.match.dl_src = packet_src_mac
        msg.match.dl_dst = packet_dst_mac

        # Set the default timeout values.
        msg.idle_timeout = DEFAULT_IDLE_TIMEOUT
        msg.hard_timeout = DEFAULT_HARD_TIMEOUT

        # For now, let's keep priorities of flow entries pertaining to 
        # the firewall function as OFP_DEFAULT_PRIORITY. The priority 
        # of the firewall functionalities on the switch shall be elevated 
        # by calling addListeners() with a non-default, larger than 0 
        # priority (check 
        # https://openflow.stanford.edu/display/ONL/POX+Wiki).
        msg.priority = of.OFP_DEFAULT_PRIORITY

#        if vale == FORWARD:
#            # Don't specify an action to indicate a packet DROP.
#            msg.actions.append(of.ofp_action_output(port = port))

        self.connection.send(msg)

        log.debug("Firewall::UploadPolicy(): Installed policy (%s,%s,%s).", 
            packet_src_mac, packet_dst_mac, value)

        return True

class firewall (EventMixin):
    '''
    Waits for OpenFlow switches to connect and makes them firewall-enabled 
    switches.
    '''
    def __init__(self):
        core.openflow.addListeners(self, priority=DEFAULT_FIREWALL_PRIORITY)

    def _handle_ConnectionUp (self, event):
        log.debug("(Firewall) Connection %s" % (event.connection,))
        Firewall(event.connection)

def launch ():
    '''
    Starting the Firewall module
    '''
    core.registerNew(firewall)

