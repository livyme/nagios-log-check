#!/usr/bin/env python
import sys
import argparse
import dns.message
import dns.query
import datetime

NAGIOS_LEVEL = {'OK': 0,
                'WARNING': 1,
                'CRITICAL': 2}
RRSIG_DATES = {'CURRENT': 0,
               'WARNING': 8,
               'CRITICAL': 6}


def _exit(code, message):
    print(message)
    sys.exit(code)


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('nameserver', help='nameserver ip address')
    args = parser.parse_args()
    return args


def main():
    args = parse_arg()
    server = args.nameserver

    request = dns.message.make_query('fhsu.edu', dns.rdatatype.RRSIG)
    response = dns.query.udp(request, server)

    answer = response.answer[0]
    type = answer.items[0]
    expiration_date = datetime.datetime.fromtimestamp(type.expiration)
    inception_date = datetime.datetime.fromtimestamp(type.inception)

    now = datetime.datetime.now()

    difference = expiration_date - now
    RRSIG_DATES['CURRENT'] = difference.days
    status_message = 'rrsig {} days until expiration.'.format(difference.days)
    additional_status_message = 'Expiration date {}\nUpdated {}'.format(expiration_date.isoformat(),
                                                                        inception_date.isoformat())

    pref_data = 'Expiration={CURRENT};{WARNING};{CRITICAL};0;30'.format(**RRSIG_DATES)
    if difference.days > 8:
        status = 'OK'
    elif difference.days > 6:
        status = 'WARNING'
    else:
        status = 'CRITICAL'
    return_message = '{}: {}|{}\n{}'.format(status, status_message, pref_data, additional_status_message)
    _exit(NAGIOS_LEVEL[status], return_message)

if __name__ == "__main__":
    main()
