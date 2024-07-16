# netconfig
Simple command line tools for creating netplan files with bonding and bridging. Full help:

```
usage: netconfig.py [-h] [-f FILENAME] [-i IP] [-b BONDING_MODE] [-g GATEWAY] [-n NAMESERVERS] [-s SEARCH] [-a]

Network configuration tool based on netplan. Usage:

options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Result filename
  -i IP, --ip IP        IP list for host. Format: 192.168.0.1/19,130.1.1.2/255.255.255.255. If None- assume dhcp
  -b BONDING_MODE, --bonding-mode BONDING_MODE
                        Bonding mode to use
  -g GATEWAY, --gateway GATEWAY
                        Manual gateway to use Format: 192.168.0.1
  -n NAMESERVERS, --nameservers NAMESERVERS
                        DNS servers for interface. Format: 8.8.8.8,8.8.4.4
  -s SEARCH, --search SEARCH
                        Search domains for interface. Format: tsnr.mtt,office.mtt
  -a                    Apply changes after exit. Works only if filename is default

```
