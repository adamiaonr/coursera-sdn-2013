from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel

import os

def output():
    """Uses the student code to compute the output for test cases."""
    outputString = ''

    print "a. Firing up Mininet"
    net = Mininet( topo=SingleSwitchTopo( 8 ), controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), autoSetMacs=True )
    net.start() 

    h3 = net.get('h3')
    h4 = net.get('h4')
    h6 = net.get('h6')
  
    print "b. Starting Test"
    # Start pings
    outputString += h3.cmd('ping', '-c3', h6.IP())
    outputString += h4.cmd('ping', '-c3', h6.IP())
    outputString += h6.cmd('ping', '-c3', h4.IP())

    print outputString.strip()

    print "c. Stopping Mininet"
    net.stop()

if __name__ == '__main__':
   # Tell mininet to print useful information
   setLogLevel('info')
   output()

