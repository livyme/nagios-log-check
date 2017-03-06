#!/usr/bin/env python
import sys
import argparse

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2


def _exit(code, message):
    print(message)
    sys.exit(code)


def load_log(filename):
    message = []
    counters = {'All': 0,
                'DEBUG': 0,
                'INFO': 0,
                'WARNING': 0,
                'ERROR': 0,
                'CRITICAL': 0}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                counters['All'] += 1
                if any(log_level in line for log_level in counters.keys()):
                    line_array = line.split('-')
                    try:
                        level = line_array[4].strip()
                    except:
                        raise Exception('Can\'t split {}'.format(line))
                    counters[level] += 1
                    if level not in ('INFO', 'DEBUG'):
                        message.append(line.strip())
    return message, counters


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='/var/log/bbsis.log',
                        help='file_location')
    if (parser.prog == "check_namecheap"):
        parser.set_defaults(file='/var/log/namecheap.log')
    elif (parser.prog == "check_follett"):
        parser.set_defaults(file="/var/log/follett_sftp.log")
    elif (parser.prog == "check_library_load"):
        parser.set_defaults(file="/var/log/librarypartonload.log")
    elif (parser.prog == "check_bbss"):
        parser.set_defaults(file="/var/log/bbss.log")
    args = parser.parse_args()
    return args


def main():
    args = parse_arg()
    log_file = args.file
    try:
        message, counters = load_log(log_file)
    except IOError:
        _exit(NAGIOS_OK, sys.exc_info()[1])
    else:
        return_message = '{INFO} info, {ERROR} error, {CRITICAL} critical, out of {All} lines '.format(
            **counters)
        return_message += 'from {}. '.format(log_file)
        if message:
            return_message += 'Last 4 messages: '
            return_message += ' '.join(message[-4:])
            code = NAGIOS_CRITICAL
        else:
            code = NAGIOS_OK
        return_message += '|All={All} INFO={INFO} WARNING={WARNING} ERROR={ERROR} CRITICAL={CRITICAL}'.format(
            **counters)
        _exit(code, return_message)


if __name__ == "__main__":
    main()

