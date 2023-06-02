#!/usr/bin/env python

"""
Create a hyrid network where contains 2 blockchains: left-Geth, right-Tendermint
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

    parser.add_argument('--nodes', default=4, type=int, 
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
    ## ------------------- initialization -------------------------
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

    ## add controllers
    for c in [ c0, c1 ]:
        net.addController(c)

    ## build mn and start network.
    net.build()
    net.start()

    ## ----------------------- pre-procedures -----------------------
    ## 1) run geth node on each hosts of left network
    for host in net.hosts[:args.nodes]:
        ## geth command
        geth_cmd = "export GOROOT=/usr/local/go; \
                export PATH=$PATH:$GOROOT/bin; \
                export GOPATH=$HOME/go_dev; \
                export PATH=$PATH:$GOPATH/bin; \
                export GOETHEREUM=$HOME/Github/go-ethereum/build; \
                export PATH=$PATH:$GOETHEREUM/bin; \
                export LD_LIBRARY_PATH=/usr/local/lib; \
                export PATH=$PATH:$LD_LIBRARY_PATH; \
                cd ../BC_network/miner"+host.name[-1]+"; \
                ./startnode.sh &>/dev/null &"
        host.cmd(geth_cmd)
    info( "\n*** Hosts are running geth node.\n" )
    for host in net.hosts[:args.nodes]:
        info(host.name, host.IP(), host.cmd('ps -aux | grep geth'), "\n")
        break;
    
    ## 2) run tendermint node on each host of right network
    for host in net.hosts[args.nodes:]:
        ## tendermint command
        node_id = int(host.name[-1])-args.nodes
        tender_cmd = "export GOROOT=/usr/local/go; \
                export PATH=$PATH:$GOROOT/bin; \
                export GOPATH=$HOME/go_dev; \
                export PATH=$PATH:$GOPATH/bin; \
                export LD_LIBRARY_PATH=/usr/local/lib; \
                export PATH=$PATH:$LD_LIBRARY_PATH; \
                cd ../Tendermint/MyChain; \
                cp genesis.json node"+str(node_id)+"/config/; \
                ./kvstore_run.sh node"+str(node_id)+" kvstore &>/dev/null & \
                cd ../../examples/tendermint_app; \
                python3.8 tender_server.py --debug --threaded -p 8088 &>/dev/null &"
        host.cmd(tender_cmd)
    info( "\n*** Hosts are running tendermint node.\n" )
    for host in net.hosts[args.nodes:]:
        info(host.name, host.IP(), host.cmd('ps -aux | grep tendermint'), "\n")
        break;
    #  python3.8 tender_server.py --debug --threaded -p 8088
    ## ----------- launch net CLI -------------
    CLI( net )

    ## ----------------------- post-procedures -----------------------
    ## 3) kill geth node before exit
    info( "\n*** Hosts are killing geth nodes.\n" )
    for host in net.hosts[:args.nodes]:
        geth_cmd = "./startnode.sh &"
        host.cmd('kill %' + geth_cmd)

    ## 4) kill tendermint node before exit
    info( "\n*** Hosts are killing geth nodes.\n" )
    for host in net.hosts[args.nodes:]:
        tender_cmd = "./kvstore_run.sh"
        host.cmd('kill %' + tender_cmd)
        tender_server = 'tender_server.py'
        host.cmd('kill %' + tender_server)
    
    ## stop net
    net.stop()
