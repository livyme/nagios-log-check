#!/usr/bin/env python
import sys
import argparse

NAGIOS_LEVEL = {'OK': 0,
                'WARNING': 1,
                'CRITICAL': 2}
LOG_TO_NAGIOS_MAPPING = {'DEBUG': 'OK',
                         'INFO': 'OK',
                         'WARNING': 'WARNING',
                         'ERROR': 'CRITICAL',
                         'CRITICAL': 'CRITICAL'}


def _exit(code, message):
    print(message)
    sys.exit(code)


def load_log(filename):
    messages = {}
    for level in NAGIOS_LEVEL.keys():
        messages[level] = []
    counter = 0
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if any(log_level in line for log_level in LOG_TO_NAGIOS_MAPPING.keys()):
                counter += 1
                line_array = line.split('-')
                try:
                    level = line_array[4].strip()
                except:
                    raise Exception('Can\'t split {}'.format(line))
                else:
                    messages[LOG_TO_NAGIOS_MAPPING[level]].append(line)
    return messages, counter


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='/var/log/bbsis.log',
                        help='file_location')
    if parser.prog == "check_namecheap":
        parser.set_defaults(file='/var/log/namecheap.log')
    elif parser.prog == "check_follett":
        parser.set_defaults(file="/var/log/follett_sftp.log")
    elif parser.prog == "check_library_load":
        parser.set_defaults(file="/var/log/librarypartonload.log")
    elif parser.prog == "check_bbss":
        parser.set_defaults(file="/var/log/bbss.log")
    args = parser.parse_args()
    return args


def main():
    args = parse_arg()
    log_file = args.file
    try:
        messages, counter = load_log(log_file)
    except IOError:
        _exit(NAGIOS_LEVEL['WARNING'], sys.exc_info()[1])
    else:
        messages_counter = {key: len(value) for key, value in messages.items()}
        messages_counter['All'] = counter
        messages_counter['log_file'] = log_file
        status = '{OK} info, {WARNING} warning, {CRITICAL} critical out of {All} lines from {log_file}.' \
                 '|INFO={OK}c;;;0;{All}'.format(**messages_counter)
        if messages['CRITICAL']:
            return_level = 'CRITICAL'
        elif messages['WARNING']:
            return_level = 'WARNING'
        else:
            return_level = 'OK'
        last_4_messages = '\n'.join(messages[return_level][-4:])
        additional_perf_data = 'WARNING={WARNING}c;1;1;0;{All} ' \
                               'CRITICAL={CRITICAL}c;1;1;0;{All}'.format(**messages_counter)
        return_message = 'Service {}: {}\n{}|{}'.format(return_level, status, last_4_messages, additional_perf_data)
        _exit(NAGIOS_LEVEL[return_level], return_message)


if __name__ == "__main__":
    main()
