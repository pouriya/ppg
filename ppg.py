#! /usr/bin/env python3

from hashlib import sha1
from base64 import b85encode, a85encode, b64encode, b32encode
from getpass import getpass
from time import sleep
from os import system
from os.path import isfile

FORMATTERS = {
    'b85': lambda string: b85encode(string),
    'a85': lambda string: a85encode(string),
    'b62': lambda string: b64encode(string).replace(b'=', b'').replace(b'/', b'').replace(b'+', b''),
    'B32': lambda string: b32encode(string).replace(b'=', b''),
    'b32': lambda string: b32encode(string).replace(b'=', b'').lower(),
    'b16': lambda string: ''.join([hex(char)[2:] for char in string]).lower().encode(),
    'B16': lambda string: ''.join([hex(char)[2:] for char in string]).upper().encode(),
    'b10': lambda string: ''.join([str(char) for char in string]).encode(),
    'b2': lambda string: ''.join([bin(char)[2:] for char in string]).encode()
}

DEFAULT_FORMATTER = 'b85'
DEFAULT_LENGTH = 32
DEFAULT_CONFIG_FILE = '/etc/services.ppg'
CLEAR_SCREEN_COMMAND = 'clear'
COLORS = {
    'red': '\033[1;31m',
    'yellow': '\033[1;33m',
    'white': '\033[1;37m',
    'grey': '\033[1;30m',
    'green': '\033[0;36m',
    'reset': '\033[0m'
}


def maybe_wait(seconds):
    if seconds < 1:
        return False
    print('{white}waiting for {}s to remove password from clipboard{reset}'.format(args.sleep, **COLORS))
    while seconds != 0:
        print('{grey}{}{reset}'.format(str(seconds), **COLORS), end=' ', flush=True)
        sleep(1)
        seconds -= 1
    print()
    return True


def maybe_resize(string, length, encoder):
    if len(string) >= length:
        return string[:length]
    # All of our formatters enlarge strings:
    return maybe_resize(FORMATTERS[encoder](string), length, encoder)


def generate_password(initialize_value, main_password, output_format, length):
    password_hash_builder = sha1()
    password_hash_builder.update(b85encode(initialize_value.encode()) + b85encode(main_password.encode()))
    return maybe_resize(FORMATTERS[output_format](password_hash_builder.digest()), length, output_format).decode()


def check_pyperclip():
    try:
        import pyperclip
    except ImportError:
        return 'Could not import/found "pyperclip" library.'
    try:
        # check lib functionality:
        pyperclip.paste()
    except Exception as reason:
        return '"pyperclip" library is not working: {}'.format(str(reason))
    return True


def parse_statement(text):
    parts = text.split(' ')
    password_format, password_length = DEFAULT_FORMATTER, str(DEFAULT_LENGTH)
    if len(parts) == 3:
        name, password_format, password_length = parts
    elif len(parts) == 2:
        name, password_format = parts
    elif len(parts) == 1:
        name = parts[0]
    else:
        return 'each line MUST be in form of NAME[ FORMATTER[ LENGTH]]'
    formatters = list(FORMATTERS.keys())
    if password_format not in formatters:
        return 'allowed formatters are {} and {}'.format(', '.join(formatters[:-1]), formatters[-1])
    if not password_length.isdigit() or int(password_length) < 1:
        return 'password length MUST be a positive integer'
    password_length = int(password_length)
    return name, password_format, password_length


def load_services(filename):
    services = []
    if not isfile(filename):
        if filename != DEFAULT_CONFIG_FILE:
            print('{red}could not found config file{reset}{white}{!r}{reset}'.format(filename, **COLORS))
        return services
    try:
        fd = open(filename)
    except Exception as reason:
        print(
            '{red}could not open file {reset}{white}{!r}{reset}: {yellow}{}{reset}'.format(filename, reason, **COLORS)
        )
        return False
    line_number = 0
    for line in fd:
        line_number += 1
        line = line.strip()
        if not line or line[0] == '#':
            continue
        parse_result = parse_statement(line)
        if type(parse_result) == str:
            print(
                '{red}syntax error in {reset}{yellow}{}{reset} {red}line{reset} {yellow}{}{reset}'.format(
                    filename,
                    line_number,
                    **COLORS
                )
            )
            print('{red}{}{reset}'.format(parse_result, **COLORS))
            return False
        services.append(parse_result)
        if len(services) > 99:
            print('{red}got more than 99 entries from {reset}{yellow}{!r}{reset}'.format(filename, **COLORS))
            return False
    return services


def maybe_print_service_names(services):
    service_count = len(services)
    if service_count != 0:
        index = 1
        # each element is (name, specific password)
        for name, _ in services:
            print(
                '{white}[{reset}{yellow}{:0>2}{reset}{white}][{reset}{green}{:^43}{reset}{white}]{reset}'.format(
                    index,
                    name,
                    **COLORS
                ),
                end=' ',
                flush=True
            )
            index += 1
            # will print 2 elements in each line:
            if index % 2 == 1:
                print()
        if index % 2 == 0:
            print()
    print()


def add_service(name, password, services):
    result = []
    for x, y in services:
        # if this name already exists, It should go to the end of list:
        if x == name:
            continue
        result.append((x, y))
    result.append((name, password))
    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='A Simple but Usable password manager.')
    parser.add_argument(
        '-f',
        '--format',
        dest='format',
        help='password format',
        choices=FORMATTERS.keys(),
        default=DEFAULT_FORMATTER
    )
    parser.add_argument(
        '-l',
        '--length',
        type=int,
        dest='length',
        help='password length',
        default=DEFAULT_LENGTH
    )
    parser.add_argument(
        '-o',
        '--output',
        dest='output',
        help='program\'s output',
        choices=['stdout', 'clipboard'],
        default='clipboard'
    )
    parser.add_argument(
        '-s',
        '--sleep',
        type=int,
        dest='sleep',
        help='how many seconds we want to keep password in clipboard',
        default=None
    )
    parser.add_argument(
        '--one-shot',
        action='store_true',
        dest='one_shot',
        help='makes response for a single query and exits'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        dest='no_color',
        help='for terminals that don\'t support our color codes'
    )
    parser.add_argument(
        '-F',
        '--file',
        dest='service_file',
        help='will read a file that contains our service names. each line in form of NAME[ FORMATTER[ LENGTH]]',
        default=DEFAULT_CONFIG_FILE
    )
    args = parser.parse_args()
    if args.no_color:
        COLORS = {k: '' for k, v in COLORS.items()}
    if args.length < 1:
        parser.exit(1, '{red}password length MUST be positive integer{reset}\n'.format(**COLORS))
    if args.sleep is not None and args.sleep < 3:
        parser.exit(1, '{red}sleep timeout MUST be positive integer bigger than 3{reset}\n'.format(**COLORS))
    if args.sleep is None:
        args.sleep = 0


    def load_last_buffer():
        return ''


    def write_buffer(text, log=True):
        if log:
            print('{yellow}{}{reset}'.format(text, **COLORS))


    if args.output == 'clipboard':
        pyperclip_check = check_pyperclip()
        if pyperclip_check is not True:
            print('{red}{}{reset}'.format(pyperclip_check, **COLORS))
            print('{red}Your password will be printed to STDOUT{reset}'.format(**COLORS))
            args.output = 'stdout'
        else:
            # override above implementations:
            def load_last_buffer():
                import pyperclip
                return pyperclip.paste()


            def write_buffer(text, log=True):
                import pyperclip
                pyperclip.copy(text)
                if log:
                    print('{yellow}Password has been copied to clipboard{reset}'.format(**COLORS))

    main_password = getpass('{white}Enter main password: {reset}'.format(**COLORS))
    if not main_password:
        print('{red}You MUST enter something as main password{reset}'.format(**COLORS))
        exit(1)
    if args.one_shot:
        service_name = input('{white}Enter service name: {reset}'.format(**COLORS))
        if not service_name:
            print('{red}You MUST enter something for service name{reset}'.format(**COLORS))
            exit(1)
        password = generate_password(service_name, main_password, args.format, args.length)
        buffer = load_last_buffer()
        write_buffer(password)
        if maybe_wait(args.sleep):
            write_buffer(buffer, False)
        exit(0)

    if args.sleep == 0:
        args.sleep = 5
    services = load_services(args.service_file)
    if services is False:
        exit(1)
    services = [(x, generate_password(x, main_password, y, z)) for x, y, z in services]
    system(CLEAR_SCREEN_COMMAND)
    while True:
        try:
            maybe_print_service_names(services)
            service_name_or_index = input('{white}Enter service name/index: {reset}'.format(**COLORS))
            if not service_name_or_index:
                print('{red}You MUST enter something for service name/index{reset}\n'.format(**COLORS))
                continue
            if service_name_or_index.isdigit():
                index = int(service_name_or_index)
                try:
                    (name, password) = services[index - 1]
                except IndexError:
                    print('{red}invalid index {reset}{yellow}{}{reset}\n'.format(index, **COLORS))
                    continue
            else:
                parse_result = parse_statement(service_name_or_index)
                if type(parse_result) == str:
                    print('{red}{}{reset}'.format(parse_result, **COLORS))
                    continue
                name, formatter, length = parse_result
                password = generate_password(name, main_password, formatter, length)
                services = add_service(name, password, services)

            print('{green}{}: {reset}'.format(name, **COLORS), end=' ', flush=True)
            buffer = load_last_buffer()
            write_buffer(password)
            if maybe_wait(args.sleep):
                write_buffer(buffer, False)
        except KeyboardInterrupt:  # Ctrl-C
            print()
            exit(1)
        system(CLEAR_SCREEN_COMMAND)
