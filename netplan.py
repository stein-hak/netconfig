import yaml
from yaml import Loader, Dumper
from execute import execute
from collections import OrderedDict

def get_ifaces():
    ret = []
    i = 0
    while 1:
        cmd = ['ethtool','-P','eth'+ str(i)]
        out, err, rc = execute(cmd)

        if rc == 0:
            ret.append(('eth'+str(i),out.split()[-1].encode('utf-8')))
        else:
            break
        i += 1
    return ret



def load_netplan():
    ret = None
    try:
        ret  = yaml.load(open('/etc/netplan/default.yaml','rb').read(),Loader=Loader)
    except:
        pass
    return ret


def convert_netmask(mask):
    if len(mask) > 2:
        ret = str(sum(bin(int(x)).count('1') for x in mask.split('.')))
    else:
        ret = mask
    return ret


class netplan:

    def __init__(self,path='/etc/netplan/default.yaml',mode=2,ip=[],mask='255.255.255.0',gateway=None,nameservers=[],search=[],bond=True,br_name='br'):
        self.path = path
        self.mode = mode
        self.ip = ip
        self.mask = mask
        self.gateway = gateway
        self.nameservers = nameservers
        self.search = search
        self.output = OrderedDict()
        self.bond = bond
        self.br_name = br_name

        self.output['network'] = OrderedDict()
        self.output['network']['renderer'] = 'networkd'
        self.output['network']['version'] = 2
        self.net_ifaces = get_ifaces()
        if len(self.net_ifaces) == 1:
            self.bond = False


    def create_ethernets(self):
        ethernets = {}
        for net in self.net_ifaces:
            ethernets[net[0]] = {'dhcp4':False,'dhcp6':False,'optional':True,'macaddress':net[1]}

        self.output['network']['ethernets'] = ethernets


    def create_bond(self,mode=1):
        ethernets = []
        if mode == 0:
            bond_type = 'balance-rr'
        elif mode == 1:
            bond_type = 'active-backup'
        elif mode == 2:
            bond_type = 'balance-xor'
        elif mode == 3:
            bond_type = 'broadcast'
        elif mode == 4:
            bond_type ='802.3ad'
        elif mode == 5:
            bond_type = 'balance-tlb'
        elif mode == 6:
            bond_type = 'balance-alb'
        else:
            bond_type = 'active-backup'


        for net in self.net_ifaces:
            ethernets.append(net[0])
        if len(ethernets) > 1:
            bond = {}
            bond['bond0'] = {'interfaces':ethernets,'dhcp4':False,'dhcp6':False,'parameters': {'mii-monitor-interval': 1, 'mode': bond_type}}
            self.output['network']['bonds'] = bond

    def create_bridge(self,name='br',bond=True):
        bridge = {}
        if not bond:
            for iface in self.net_ifaces:
                br_name = name + str(self.net_ifaces.index(iface))
                bridge[br_name] = {'parameters': {'forward-delay': 0, 'stp': False}}
        else:
            br_name = name + '0'
            bridge[br_name] = {'parameters': {'forward-delay': 0, 'stp': False}}

        if self.ip:
            ip_addrs= []
            for addr in self.ip:
                try:
                    ip = addr.split('/')[0]
                    netmask = addr.split('/')[1]
                except:
                    ip = addr.split('/')[0]
                    netmask = '24'

                ip_addrs.append(ip+'/'+convert_netmask(netmask))




            bridge[name+'0']['dhcp4'] = False
            bridge[name+'0']['dhcp6'] = False
            bridge[name+'0']['addresses'] = ip_addrs
            if self.gateway:
                bridge[name+'0']['gateway4'] = self.gateway

        else:
            for br in bridge.keys():
                bridge[br]['dhcp4'] = True
                bridge[br]['dhcp6'] = False
                bridge[br]['macaddress'] = self.net_ifaces[int(br.strip(name))][1]

        if bond:
            bridge[name+'0']['interfaces'] = ['bond0']
        else:
            for br in bridge.keys():
                bridge[br]['interfaces']= [self.net_ifaces[int(br.strip(name))][0]]

        if self.nameservers:
            bridge[name+'0']['nameservers'] = {}
            bridge[name+'0']['nameservers']['addresses'] = self.nameservers
            if self.search:
                bridge[name+'0']['nameservers']['search'] = self.search

        self.output['network']['bridges'] = bridge


    def create_config(self,path):

        self.create_ethernets()
        if self.bond:
            self.create_bond(mode=self.mode)
        self.create_bridge(name=self.br_name,bond=self.bond)

        f = open(path, 'wb')

        yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_mapping('tag:yaml.org,2002:map', data.items()))

        ya = yaml.dump(self.output,Dumper=Dumper)

        f.write(ya.encode('utf-8'))
        f.close()





if __name__ == '__main__':
    net = netplan(nameservers=['8.8.8.8','4.4.4.4'],search=['tsnr.mtt'],br_name='xvbr',bond=False)
    net.create_config('/root/default1.yaml')
