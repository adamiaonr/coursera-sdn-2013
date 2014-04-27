#!/usr/bin/python

'''
Coursera:
- Software Defined Networking (SDN) course
-- Module 3 Programming Assignment

Professor: Nick Feamster
Teaching Assistant: Muhammad Shahbaz
'''

import math

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.link import TCLink

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # Add your logic here ...
        self.fanout = fanout

        datacenterNodeList = []
        layerNodeList = []

        # we assume 4 layers: core, aggregation, edge, host
        layers = {0:'core', 1:'aggregation', 2:'edge', 3:'host'}

        # collect the performance parameters for links between datacenter 
        # layers
        layersOptsList = {1:linkopts1, 2:linkopts2, 3:linkopts3}

        # for each non-core layer, create the appropriate nodes (incl. 
        # appropriate number of nodes) and appropriate connections
        for level, layer in sorted(layers.iteritems()):

            # add nodes, for each level fanout^(level - 1) nodes
            for i in irange(1, fanout**(level)):

                # we have to distinguish between nodes 
                # FIXME: there's an ugly if statement here which checks for 
                # a specific key value - 'host' -to call addHost() instead
                #print "Adding node {var1}{var2}".format(var1 = layer[0],var2 = i)

                if layer == 'host':
                    node = self.addHost("{var1}{var2}".format(var1 = layer[0],var2 = i))
                else:
                    node = self.addSwitch("{var1}{var2}".format(var1 = layer[0],var2 = i))

                layerNodeList.append(node)

                # add links to respective parents on previous layer
                # FIXME: another ugly if statement
                if layer != 'core':

                    # sublevel... for the lack of a better word...
                    sublevel = int(math.ceil(float(i) / float(fanout)) - 1)

                    #print "linkin' ", node, "with ", datacenterNodeList[level - 1][sublevel]
                    self.addLink(node, datacenterNodeList[level - 1][sublevel], **layersOptsList[level])

            datacenterNodeList.append(list(layerNodeList))
            layerNodeList[:] = []

#topos = { 'custom': ( lambda: CustomTopo() ) }

def simpleTest():

    "Set up link parameters"
    print "a. Setting link parameters"
    "--- core to aggregation switches"
    linkopts1 = {'bw':50, 'delay':'5ms'}
    "--- aggregation to edge switches"
    linkopts2 = {'bw':30, 'delay':'10ms'}
    "--- edge switches to hosts"
    linkopts3 = {'bw':10, 'delay':'15ms'}
  
    "Creating network and run simple performance test"
    print "b. Creating Custom Topology"
    topo = CustomTopo(linkopts1, linkopts2, linkopts3, fanout=3)

    print "c. Firing up Mininet"
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    h1 = net.get('h1')
    h27 = net.get('h27')
  
    print "d. Starting Test"
    # Start pings
    outputString = h1.cmd('ping', '-c6', h27.IP())
    
    print "e. Stopping Mininet"
    net.stop()

    print outputString.strip()

if __name__ == '__main__':
   # Tell mininet to print useful information
   setLogLevel('info')
   simpleTest()
