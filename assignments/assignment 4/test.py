from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController   
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel

import os

# My network topology
class MyTopo(Topo):
    "1 switch and 3 host topology with varying delays"

    def __init__(self, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        s1 = self.addSwitch('s1')

        h1 = self.addHost('h1')
        self.addLink(h1, s1)
        h2 = self.addHost('h2')
        self.addLink(h2, s1, delay='200ms')
        h3 = self.addHost('h3')
        self.addLink(h3, s1)

def output():
    """Uses the student code to compute the output for test cases."""
    outputString = ''

    print "a. Firing up Mininet"
    net = Mininet(topo=MyTopo(), controller=lambda name: RemoteController( 'c0', '127.0.0.1' ), host=CPULimitedHost, link=TCLink)
    net.start() 

    h1 = net.get('h1')
  
    print "b. Starting Test"
    # Start pings
    outputString += h1.cmdPrint('ping', '-c9', '10.0.0.100')

    print outputString.strip()

    print "c. Stopping Mininet"
    net.stop()

if __name__ == '__main__':
   # Tell mininet to print useful information
   setLogLevel('info')
   output()

