import re
import os
import networkx as nx 
from jinja2 import Environment, FileSystemLoader
from _yaml import yaml
from pprint import pprint
from operator import add


def remove_duplicates(l):
    return list(set(l))

def getDutList():
    try:  
        dutInfo =[]
        with open('netlist') as input_data:
            # Skips text before the beginning of the interesting block:
            for line in input_data:
                if line.strip() == 'dut:':  # Or whatever test is needed
                    break
                # Reads text until the end of the block:
            for line in input_data:  # This keeps reading the file
                if line.strip() == ':dut':
                    break
                #print line  # Line is extracted (or block_of_lines.append(line), etc.)
                dutInfo.append(line.strip())
    except:
        print 'Exeption: check your netlist.'
    return dutInfo

def getDutInfo(dut):
    dl=getDutList()        
    dlElement = []
    dlNode = []
    dutInfo =[]
    for line in dl:
        if re.search('\S', line):
            dlElement = str.split(line)
            dutInfo.append([dlElement[1],dlElement[2],dlElement[3],dlElement[4]])
    #print "dutInfo:"
    #pprint (dutInfo)
    
    MyDutInfo = []
    for i in dutInfo:
        if i[0] == dut:
            MyDutInfo.append([i[0],i[1],i[2],i[3]])
    #print 'MyDutInfo'
    #pprint (MyDutInfo)
    return MyDutInfo
   
def getNetworklist():
        # parsing netlist    
    try:  
        nl =[]
        with open('netlist') as input_data:
            for line in input_data:
                if line.strip() == 'netlist:':  # Or whatever test is needed
                    break
            for line in input_data:  # This keeps reading the file
                if line.strip() == ':netlist':
                    break
                nl.append(line.strip())
    except:
        print 'Exeption: check your netlist.'
    return nl



def getSegment():
    nl=getNetworklist()        
    nlElement = [] 
    segment = []   
    for line in nl:
        if re.search('\S', line):
            nlElement = str.split(line)
            segment.append([nlElement[0],nlElement[1]])
    return sorted(segment)

def getSegmentDut(dut):
    segment = getSegment()
    SegmentDut = []
    for i in segment:
        if i[0] == dut:
            SegmentDut.append(i[1])
        if i[1] == dut:
            SegmentDut.append(i[0])
    if SegmentDut == []:
        print 'no Segment dut'
    else: 
        return SegmentDut


def getDutSegmentInfo(dut):
    nl=getNetworklist()        
    nlElement = []
    segmentIP = []
    segmentPort = []  
    segmentEncap = []
    segmentVlan = []
    segmentOspf = []
    segmentRtrInstance = []
    for line in nl:
        if re.search('\S', line):
            nlElement = str.split(line)
            segmentIP.append([nlElement[2],nlElement[3]])
            segmentPort.append([nlElement[5],nlElement[6]])
            segmentEncap.append([nlElement[7],nlElement[7]])
            segmentVlan.append([nlElement[8],nlElement[8]])
            segmentRtrInstance.append([nlElement[9],nlElement[9]])
            segmentOspf.append([nlElement[10],nlElement[10]])
    segment=getSegment()
    segmentIP = map(add, segment, segmentIP)
    for item in segmentIP:
        if item[2] == 'auto':
            if item[0] > item[1]:
                item[2] = '10.'+item[1]+'.'+item[0]+'.2'
            else:
                item[2] = '10.'+item[0]+'.'+item[1]+'.2'
                
        if item[3] == 'auto':
            if item[0] > item[1]:
                item[3] = '10.'+item[1]+'.'+item[0]+'.1'
            else:
                item[3] = '10.'+item[0]+'.'+item[1]+'.1'     
    segmentInfo = map(add, segmentIP, segmentPort)
    segmentInfo = map(add, segmentInfo, segmentEncap)
    segmentInfo = map(add, segmentInfo, segmentVlan)
    segmentInfo = map(add, segmentInfo, segmentRtrInstance)
    segmentInfo = map(add, segmentInfo, segmentOspf)

    MyDutSegmentInfo = []
    for i in segmentInfo:
        if i[0] == dut:
            MyDutSegmentInfo.append([i[2],i[4],i[6],i[8],i[10],i[12]])
        if i[1] == dut:
            MyDutSegmentInfo.append([i[3],i[5],i[7],i[9],i[11],i[13]])
    #pprint (MyDutSegmentInfo)
      
    if MyDutSegmentInfo == []:
        print 'no Segment dut Info, check Netlsit'
    else: 
        return MyDutSegmentInfo  


def getOctetIP(ip):
    p = re.compile("\.")
    return p.split(ip)
 
 
def createYaml(dut):   
    MydutInfo = getDutInfo(dut)
    SegmentDutSegmentDutInfo = zip(getSegmentDut(dut), getDutSegmentInfo(dut))
    nl=getNetworklist()
    segment=getSegment()
    
    x = open('configVar.yaml','w')
    # Create yaml for management
    x.write('management:'+'\n')
    x.write('  sysIP: '+'1.1.1.'+getOctetIP(MydutInfo[0][1])[3]+'/32'+'\n')
    x.write('\n')
    
    # Create yaml for port
    x.write('ports:'+'\n')
    for item in SegmentDutSegmentDutInfo:
        x.write('  - id: '+item[1][1]+'\n')
        x.write('    encap: '+item[1][2]+'\n')
        x.write('    vlan: '+item[1][3]+'\n')
    x.write('\n')
    
    # Create yaml for router interface    
    x.write('router_interface:'+'\n')
    for item in SegmentDutSegmentDutInfo:
        x.write('  - IntName: '+item[0][0]+'\n')
        x.write('    IP: '+item[1][0]+'/30'+'\n')
        x.write('    port: '+item[1][1]+'\n')
        if item[1][2] == 'null':
            x.write('    encapNull: True '+'\n')
            x.write('    encap: '+item[1][2]+'\n')
        else:
            x.write('    encap: '+item[1][2]+'\n')
        x.write('    vlan: '+item[1][3]+'\n')
        x.write('    rtrInstance: '+item[1][4]+'\n')
        x.write('    ospfArea: '+item[1][5]+'\n')      
    
    
    # Create yaml for router mpls    
    x.write('\n')
    x.write('router_mpls:'+'\n')
    for item in SegmentDutSegmentDutInfo:
        x.write('  - peerNode: '+getOctetIP(getDutInfo(item[0])[0][1])[3]+'\n' )
        x.write('    IntName: '+item[0][0]+'\n')
        x.write('    peerSysIP: '+'1.1.1.'+getOctetIP(getDutInfo(item[0])[0][1])[3]+'/32'+'\n' )

    x.close()
def RenderConfig(dut):   
    createYaml(dut)
    yamlConfig = yaml.load(open('configVar.yaml'))
    ENV = Environment(loader=FileSystemLoader('./SROS-Templates/'))
    template = ENV.get_template('routerInterface.j2')
    pprint (yamlConfig)
    #print(template.render(yamlConfig["management"]))
    pprint( [i for n, i in enumerate(yamlConfig["ports"]) if i not in yamlConfig["ports"][n + 1:]] )
    print(template.render(config=yamlConfig))

def main():
    dut = '2'
    RenderConfig(dut) 

main()


