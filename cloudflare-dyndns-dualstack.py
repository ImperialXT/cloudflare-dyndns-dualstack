import os
import argparse
import sys
import netifaces
import requests
import CloudFlare

sys.path.insert(0, os.path.abspath('..'))

def my_ipv4_address():

    url = 'https://ipv4.icanhazip.com'
    try:
        ip_address = requests.get(url).text.rstrip()
    except:
        exit('%s: failed' % (url))
    if ip_address == '':
        exit('%s: failed' % (url))

    ip_address_type = "A"

    return ip_address, ip_address_type

def my_ipv6_address(interface):
    
    try:
        ip_address = netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['addr']
    except:
        exit('Getting IPv6 from interface failed')
    if ip_address == '':
        exit("Didn't get a valid address back.")

    ip_address_type = "AAAA"

    return ip_address, ip_address_type


def do_dns_update(cf, zone_name, zone_id, dns_name, ip_address, ip_address_type):

    try:
        params = {'name':dns_name, 'match':'all', 'type':ip_address_type}
        dns_records = cf.zones.dns_records.get(zone_id, params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones/dns_records %s - %d %s - api call failed' % (dns_name, e, e))

    updated = False

    # update the record - unless it's already correct
    for dns_record in dns_records:
        old_ip_address = dns_record['content']
        old_ip_address_type = dns_record['type']

        if ip_address_type not in ['A', 'AAAA']:
            # we only deal with A / AAAA records
            continue

        if ip_address == old_ip_address:
            print('UNCHANGED: %s %s' % (dns_name, ip_address))
            updated = True
            continue

        # Yes, we need to update this record - we know it's the same address type

        dns_record_id = dns_record['id']
        dns_record = {
            'name':dns_name,
            'type':ip_address_type,
            'content':ip_address
        }
        try:
            dns_record = cf.zones.dns_records.put(zone_id, dns_record_id, data=dns_record)
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('/zones.dns_records.put %s - %d %s - api call failed' % (dns_name, e, e))
        print('UPDATED: %s %s -> %s' % (dns_name, old_ip_address, ip_address))
        updated = True

    if updated:
        return

    # no exsiting dns record to update - so create dns record
    dns_record = {
        'name':dns_name,
        'type':ip_address_type,
        'content':ip_address
    }
    try:
        dns_record = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones.dns_records.post %s - %d %s - api call failed' % (dns_name, e, e))
    print('CREATED: %s %s' % (dns_name, ip_address))

def main():

    parser = argparse.ArgumentParser(
            description='DynDNS Script for compatabile with Dualstack environments for use with CloudFlare',
    )
    parser.add_argument(
            'dns_name',
            help='the dns_name you want to update in CloudFlare e.g dynamic.example.domain',
    )
    parser.add_argument(
            '-i', '--interface', action='store', dest='interface', default='eno1',
            help='What interface on this machine should we use to get your IPv6'
    )

    # We only want one or the other to be disabled.
    # If you disable both there's no point in using the script at all
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
            '--no-ipv6', action='store_false', dest='ipv6', default=True,
            help='Disable IPv6',
    )
    group.add_argument(
            '--no-ipv4', action='store_false', dest='ipv4', default=True,
            help='Disable IPv4'
    )
    args = parser.parse_args()
    ipv4 = args.ipv4
    ipv6 = args.ipv6
    dns_name = args.dns_name
    interface = args.interface
    host_name, zone_name = dns_name.split('.', 1)

    if ipv4:
        ipv4_address, ipv4_address_type = my_ipv4_address()
        print('MY IPv4 Addresses: %s %s' % (dns_name, ipv4_address))
    if ipv6:
        ipv6_address, ipv6_address_type = my_ipv6_address(interface)
        print('MY IPv6 Addresses: %s %s' % (dns_name, ipv6_address))
    
    cf = CloudFlare.CloudFlare()

    # grab the zone identifier
    try:
        params = {'name':zone_name}
        zones = cf.zones.get(params=params)
    except CloudFlare.exceptions.CloudFlareAPIError as e:
        exit('/zones %d %s - api call failed' % (e, e))
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))

    if len(zones) == 0:
        exit('/zones.get - %s - zone not found' % (zone_name))

    if len(zones) != 1:
        exit('/zones.get - %s - api call returned %d items' % (zone_name, len(zones)))

    zone = zones[0]

    zone_name = zone['name']
    zone_id = zone['id']

    if ipv4:
        do_dns_update(cf, zone_name, zone_id, dns_name, ipv4_address, ipv4_address_type)
    if ipv6:
        do_dns_update(cf, zone_name, zone_id, dns_name, ipv6_address, ipv6_address_type)
    exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exiting due to keyboard interupt', file=sys.stderr)
        sys.exit(1)
