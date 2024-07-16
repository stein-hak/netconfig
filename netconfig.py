#!/usr/bin/python3

import sys
sys.path.append('/opt/lib')
import argparse
from netplan import netplan
from execute import execute



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Network configuration tool based on netplan. Usage:')
    parser.add_argument('-f', '--filename', default='/etc/netplan/default.yaml', help='Result filename')
    parser.add_argument('-i', '--ip', help='IP list for host. Format: 192.168.0.1/19,130.1.1.2/255.255.255.255. If None- assume dhcp')
    parser.add_argument('-b', '--bonding-mode', type=int, default=2, help='Bonding mode to use')
    parser.add_argument('-g','--gateway',help='Manual gateway to use Format: 192.168.0.1')
    parser.add_argument('-n','--nameservers',help='DNS servers for interface. Format: 8.8.8.8,8.8.4.4')
    parser.add_argument('-s','--search',help='Search domains for interface. Format: tsnr.mtt,office.mtt')
    parser.add_argument('-a',action='store_true',help='Apply changes after exit. Works only if filename is default')

    args = parser.parse_args()

    ip = []
    if args.ip:
        ip =  args.ip.split(',')


    dns = []

    if args.nameservers:
        dns = args.nameservers.split(',')

    search = []
    if args.search:
        search = args.search.split(',')


    net = netplan(ip=ip,gateway=args.gateway,nameservers=dns,search=search,mode=args.bonding_mode)

    net.create_config(args.filename)

    print('Created new network config in file %s' % args.filename)

    if args.a and args.filename == '/etc/netplan/default.yaml':
        out, err, rc = execute(['netplan','apply'])
        if rc == 0:
            print('Settings applied. If bonding mode was changed, reboot is required')
        else:
            print('Failed to apply network changes')
            print(err)




