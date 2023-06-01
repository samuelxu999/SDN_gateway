#!/usr/bin/env python

"""
Create a main network where contains 2 local controllers and 1 remote controllers.
"""
import sys
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController, CPULimitedHost
from mininet.topolib import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.util import custom
from argparse import ArgumentParser

class MultiSwitch( OVSSwitch ):
    '''
    Custom Switch() subclass that connects to different controllers
    '''
    def start( self, controllers ):
        return OVSSwitch.start( self, [ cmap[ self.name ] ] )

class myTopo(Topo):
    def build(self, count=1):
        ## create custom host and add the network
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

def define_and_get_arguments(args=sys.argv[1:]):
    parser = ArgumentParser(description="Run mn test net.")

    parser.add_argument('--nodes', default=2, type=int, 
                        help="Host node number for a sub-network.")

    parser.add_argument('--cpu', default=1.0, type=float, 
                        help="Host node cup limitation.")

    args = parser.parse_args(args=args)
    return args

if __name__ == '__main__':
    setLogLevel( 'info' )
    ## get arguments
    args = define_and_get_arguments()

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
    topo = myTopo(args.nodes)

    ## new a mn instance
    host = custom( CPULimitedHost, sched='cfs', cpu=args.cpu )
    net = Mininet( topo=topo, host=host, switch=MultiSwitch, build=False, waitConnected=True )
    # net = Mininet( topo=topo, switch=MultiSwitch, build=False, waitConnected=True )

    ## add controllers
    for c in [ c0, c1 ]:
        net.addController(c)

    ## build mn and start network.
    net.build()
    net.start()
    ## run geth node on each host
    for host in net.hosts:
        ## tendermint command ./kvstore_run.sh node" +host.name[-1]+" kvstore &>/dev/null &"
                        # ./init_node.sh node"+host.name[-1]+" 
        tender_cmd = "export GOROOT=/usr/local/go; \
                export PATH=$PATH:$GOROOT/bin; \
                export GOPATH=$HOME/go_dev; \
                export PATH=$PATH:$GOPATH/bin; \
                export LD_LIBRARY_PATH=/usr/local/lib; \
                export PATH=$PATH:$LD_LIBRARY_PATH; \
                cd ../Tendermint/MyChain; \
                cp genesis.json node"+host.name[-1]+"/config/; \
                ./kvstore_run.sh node"+host.name[-1]+" kvstore &>/dev/null &"
        # tender_cmd="echo $PATH"
        host.cmd(tender_cmd)
    info( "\n*** Hosts are running tendermint node.\n" )
    for host in net.hosts:
        info(host.name, host.IP(), host.cmd('ps -aux | grep tendermint'), "\n")
        break;
    CLI( net )
    ## kill tendermint node before exit
    info( "\n*** Hosts are killing tendermint nodes.\n" )
    for host in net.hosts:
        tender_cmd = './kvstore_run.sh'
        host.cmd('kill %' + tender_cmd)
    net.stop()
