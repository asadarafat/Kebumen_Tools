# Kebumen_Tools
# Create SROS router configuration as easy as 1,2,3

##############################################################################
# STEP 1: List all nodes
# 
# SYNTAX:
#    set node(a) {managementIP SystemIP type}
#
# DESCRIPTION:
#    systemIP: you can specify an IP or leave it "auto" and let the "topobuilder"
#              assign IP for you, with defaultIP "1.1.1.$host", where $host is
#              the host of the management IP
#    type:     if it's not specified, it's considered 7x50
###############################################################################
dut:
node 111  135.241.247.11 auto 		7x50
node 222  135.241.247.22 2.2.2.22 	7x50
node 333  135.241.247.33 auto 		7x50
node 444  135.241.247.44 auto 		7x50
:dut

###############################################################################
# STEP 2: Build the netlist how is cable connected among listed nodes above.
#
# SYNTAX:
#    {node1 node2 ip1 ip2 phyType port1 port2 encap ident ospf-area isis-level}
# 
# DESCRIPTION:
#    node1, node2: identify which node. The node ID must match what is used
#                  the list of nodes in STEP 1
#    ip1, ip2:     you can specify the IP interface or leave it "auto" and
#                  let the "topobuilder" assign it for you.
#                  If you specify it manually, the format is "ip/prefixLength"
#                  (e.g., 10.12.13.2/30)
#    port1, port2: port or a list of port when the phyType is lag
#                  port list has format {lag-<id> {member1 member2 ...}}
#    phyType:      fe, ge, 10ge, lag
#    encap:        null or dot1q
#    ident:        none or vlanID if the encap is dot1q
#    instance:     router instance 
#    ospf-area:    if it's not specified, it's considered area 0
#    isis-level:   1, 2, or 1/2. If it's not specified, it's considered as 1/2 @aarafat-tag: To be done
#                  This is level-capability per link (i.e., segment), which 
#                  is 1/2 by default
###############################################################################
netlist:
111 222 auto auto ge 1-2 2-1 null  10 1 0 2
333 444 auto auto ge 3-4 4-3 dot1q 10 0 0 2
111 333 auto auto ge 1-3 3-1 dot1q 10 0 2 1
111 444 auto auto ge 1-4 4-1 dot1q 10 0 0 2
:netlist

##############################################################################
# STEP 3: Tell the "topobuilder" what to build., such as configure the port,
#         network interface, ospf, isis, mpls, bfd, authentication key, etc.
#        
#         Auto Mesh Tunnel is also supported
# DESCRIPTION:
#    ldp below refers to interface LDP.
# 
# @aarafat-tag: To be done
###############################################################################
