#!/usr/bin/env python

"""
Create a main network where contains 2 local controllers and 1 remote controllers.
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.topolib import Topo
from mininet.log import setLogLevel
from mininet.cli import CLI

class MultiSwitch( OVSSwitch ):
    '''
    Custom Switch() subclass that connects to different controllers
    '''
    def start( self, controllers ):
        return OVSSwitch.start( self, [ cmap[ self.name ] ] )

class myTopo(Topo):
    def build(self, count=1):
        hosts = [ self.addHost( 'h%d' % i )                                                                                   
                  for i in range( 1, 2*count + 1 ) ] 

        ## create s1 for left network
        s1 = self.addSwitch('s1')
        for h in hosts[:count]:
            self.addLink( h, s1 ) 
        
        ## create s2 for right network
        s2 = self.addSwitch('s2')
        for h in hosts[count:]:
            self.addLink( h, s2 ) 

        ## create s3 for gateway controller 
        s3 = self.addSwitch('s3')
        self.addLink(s1, s3)  
        self.addLink(s2, s3) 


if __name__ == '__main__':
    setLogLevel( 'info' )

    '''
    Two local and one "external" controller (which is actually c0)
    Ignore the warning message that the remote isn't (yet) running
    '''
    c0 = Controller( 'c0', port=6633 )
    c1 = Controller( 'c1', port=6634 )

    ## add one remote controller
    c2 = RemoteController( 'c2', ip='128.226.88.197', port=6633 )

    cmap = { 's1': c0, 's2': c1, 's3': c2 }

    ## initialize topology templace
    topo = myTopo(4)

    ## new a mn instance
    net = Mininet( topo=topo, switch=MultiSwitch, build=False, waitConnected=True )

    ## add controllers
    for c in [ c0, c1 ]:
        net.addController(c)

    ## build mn and start network.
    net.build()
    net.start()
    CLI( net )
    net.stop()
