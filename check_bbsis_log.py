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
            if line:
                counter += 1
                if any(log_level in line for log_level in LOG_TO_NAGIOS_MAPPING.keys()):
                    line_array = line.split('-')
                    try:
                        level = line_array[4].strip()
                    except:
                        raise Exception('Can\'t split {}'.format(line))
                    messages[LOG_TO_NAGIOS_MAPPING[level]].append(line)
    return messages, counter


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
        messages, counter = load_log(log_file)
    except IOError:
        _exit(NAGIOS_LEVEL['WARNING'], sys.exc_info()[1])
    else:
        messages_length = {key:len(value) for key,value in messages.items()}
        messages_length['All'] = counter
        return_message = '{OK} info, {WARNING} error, {CRITICAL} critical out of {All} lines '.format(
            **messages_length) + 'from {}.'.format(log_file)
        return_message += '|Critical={CRITICAL}c;1;1;0;{All}\n'.format(**messages_length)
        if messages['CRITICAL']:
            code = NAGIOS_LEVEL['CRITICAL']
            return_message += '\n'.join(messages['CRITICAL'][-4:])
        elif messages['WARNING']:
            code = NAGIOS_LEVEL['WARNING']
            return_message += '\n'.join(messages['WARNING'][-4:])
        else:
            code = NAGIOS_LEVEL['OK']
            return_message += '\n'.join(messages['OK'][-4:])
        return_message += '|WARNING={WARNING}c;1;1;0;{All} OK={OK}c;{All};{All};0;{All}'.format(
            **messages_length)
        _exit(code, return_message)



if __name__ == "__main__":
    main()
