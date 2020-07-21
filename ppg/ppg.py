#! /usr/bin/env python3

from hashlib import sha1
from base64 import b85encode, a85encode, b64encode, b32encode
from getpass import getpass
from collections import namedtuple
from time import sleep


def sanitize_b85(string):
    return b85encode(string).decode()


def sanitize_a85(string):
    return a85encode(string).decode()


def sanitize_b64(string):
    # it's not a complete base64. we remove padding and '+' so it contains only A-z, a-z and 0-9:
    return b64encode(string).replace(b'=', b'').replace(b'/', b'').replace(b'+', b'').decode()


def sanitize_b32(string):
    # Remove base32 padding character:
    return b32encode(string).replace(b'=', b'').decode()


def sanitize_b16(string):
    return ''.join([hex(char)[2:] for char in string])


def sanitize_b10(string):
    return ''.join([str(char) for char in string])


def sanitize_b2(string):
    return ''.join([bin(char)[2:] for char in string])


def sanitize(string, output_format):
    if output_format == 'b85':
        output = sanitize_b85(string)
    elif output_format == 'a85':
        output = sanitize_a85(string)
    elif output_format == 'b64':
        output = sanitize_b64(string)
    elif output_format == 'b32':
        output = sanitize_b32(string)
    elif output_format == 'b16':
        output = sanitize_b16(string)
    elif output_format == 'b10':
        output = sanitize_b10(string)
    elif output_format == 'b2':
        output = sanitize_b2(string)
    else:
        raise ValueError('$Unknown output format {!r}'.format(output_format))
    return output


def maybe_resize(string, length):
    if string is '':
        raise ValueError('$got empty string for resize')
    string_length = len(string)
    if string_length >= length:
        return string[:length]
    new_string = string
    new_string_length = string_length
    reminder = 0
    while True:
        for char in string[::-1]:
            if ord(char) % 2 != reminder:
                continue
            new_string += char
            new_string_length += 1
            if new_string_length == length:
                return new_string
        if reminder == 0:
            reminder = 1
        else:
            reminder = 0


def generate_password(initialize_value, main_password, output_format, length):
    password_hash_builder = sha1()
    password_hash_builder.update(b85encode(initialize_value.encode()) + b85encode(main_password.encode()))
    return maybe_resize(sanitize(password_hash_builder.digest(), output_format), length)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='A simple but usable password generator.')
    parser.add_argument(
        '-f',
        '--format',
        dest='format',
        help='password format',
        choices=['b85', 'a85', 'b64', 'b32', 'b16', 'b10', 'b2'],
        default='b85'
    )
    parser.add_argument(
        '-l',
        '--length',
        type=int,
        dest='length',
        help='password length',
        default=32
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
        default=0
    )
    parser.add_argument(
        '-L',
        '--loop',
        action='store_true',
        dest='loop',
        help='start program in \'loop\' mode',
    )
    parser.add_argument(
        '--no-color',
        action='store_false',
        dest='colorize',
        help='for terminals that don\'t support our color codes'
    )
    parser.add_argument(
        '-F',
        '--file',
        dest='service_file',
        help='in \'loop\' mode will read a file that contains our service names',
        default=None
        # default='/etc/ppg_services.txt'
    )
    args = parser.parse_args()

    Colors = namedtuple('Colors', ['red', 'yellow', 'white', 'grey', 'green', 'reset'])
    colors = Colors(red='', yellow='', white='', grey='', green='', reset='')
    if args.colorize:
        colors = Colors(
            red='\033[1;31m',
            yellow='\033[1;33m',
            white='\033[1;37m',
            grey='\033[1;30m',
            green='\033[0;36m',
            reset='\033[0m'
        )

    if args.length < 1:
        parser.exit(1, colors.red + 'password length MUST be a positive integer\n' + colors.reset)

    def maybe_raise(exception):
        # It's our custom exception, we can print it and skip:
        if str(exception)[0] == '$':
            print(colors.red + str(exception)[1:] + colors.reset)
        else:
            raise exception

    # The real shit starts here:
    try:
        # Check 'pyperclip' lib if we want to be able to paste password(s):
        if args.output == 'clipboard':
            try:
                import pyperclip
            except ImportError:
                print(colors.red + 'Could not import/found "pyperclip" library.' + colors.reset)
                print(colors.red + 'Your password will be printed to STDOUT' + colors.reset)
                args.output = 'stdout'
        if args.output == 'clipboard':
            try:
                # check lib functionality:
                pyperclip.paste()
            except Exception as error:
                print(colors.red + '"pyperclip" library is not working: {}'.format(str(error)) + colors.reset)
                print(colors.red + 'Your password will be printed to STDOUT'.format(str(error)) + colors.reset)
                args.output = 'stdout'

        main_password = getpass(colors.white + 'Enter password: ' + colors.reset)
        if not main_password:
            raise ValueError('$You MUST enter something for password')

        if not args.loop:
            service_name = input(colors.white + 'Enter service name: ' + colors.reset)
            if not service_name:
                raise ValueError('$You MUST enter something for service name')
            password = generate_password(service_name, main_password, args.format, args.length)
            if args.output == 'stdout':
                print(colors.yellow + password + colors.reset)
            else:
                clipboard_buffer = pyperclip.paste()
                pyperclip.copy(password)
                print(colors.yellow + 'Password has been copied to clipboard' + colors.reset)
                if args.sleep > 0:
                    print(colors.white + 'waiting for {}s to remove password from clipboard'.format(args.sleep) + colors.reset)
                    while args.sleep != 0:
                        print(colors.grey + str(args.sleep) + colors.reset, end=' ', flush=True)
                        sleep(1)
                        args.sleep -= 1
                    print()
                    pyperclip.copy(clipboard_buffer)
            exit(0)

        # define functions for 'loop' mode:
        def maybe_print_service_names(service_names):
            service_count = len(service_names)
            if service_count != 0:
                service_id = 1
                # each element is (name, specific password)
                for service_name, _ in service_names:
                    print(
                        colors.white +
                        '[' +
                        colors.reset +
                        colors.yellow +
                        '{:>2}'.format(service_id) +
                        colors.reset +
                        colors.white +
                        '][' +
                        colors.reset +
                        colors.green +
                        '{:^43}'.format(service_name) +
                        colors.reset +
                        colors.white +
                        ']' +
                        colors.reset,
                        end=' ',
                        flush=True
                    )
                    service_id += 1
                    # will print 2 elements in each line:
                    if service_id % 2 == 1:
                        print()
                if service_id % 2 == 0:
                    print()
            print()


        def maybe_read_service_names(filename, colors, main_password, output_format, length):
            service_names = []
            if filename:
                try:
                    fd = open(filename)
                except Exception as error:
                    print(colors.red + 'could not open service file {!r}: {}'.format(filename, error) + colors.reset)
                    return service_names
                for line in fd:
                    line = line.replace('\n', '').replace('\r', '')
                    if line:
                        if line[0] == '#':
                            continue
                        service_names.append((line, generate_password(line, main_password, output_format, length)))
            return service_names


        def maybe_add_service_name(service_name, password, service_names):
            result = []
            for x, y in service_names:
                if x == service_name:
                    continue
                result.append((x, y))
            result.append((service_name, password))
            return result

        # start 'loop' mode:
        service_names = maybe_read_service_names(args.service_file, colors, main_password, args.format, args.length)
        while True:
            maybe_print_service_names(service_names)
            service_name_or_id = input(colors.white + 'Enter service name/id: ' + colors.reset)
            if not service_name_or_id:
                print(colors.red + 'You MUST enter something for service name/id', colors.reset)
                print()
                continue

            if service_name_or_id.isdigit():
                service_id = int(service_name_or_id)
                if service_id < 1:
                    print(colors.red + 'service id MUST be positive integer', colors.reset)
                    print()
                    continue
                try:
                    (service_name, password) = service_names[service_id-1]
                except IndexError:
                    print(colors.red + 'invalid id {}'.format(service_id), colors.reset)
                    print()
                    continue
            else:
                parts = service_name_or_id.split(':')
                if len(parts) > 3 or len(parts) == 0:
                    print(colors.red + 'service name MUST be in form of SERVICE_NAME[:FORMAT[:LENGTH]]', colors.reset)
                    print()
                    continue
                output_format = args.format
                length = str(args.length)
                if len(parts) == 3:
                    service_name, output_format, length = parts
                elif len(parts) == 2:
                    service_name, output_format = parts
                else:
                    service_name = parts[0]
                if length.isdigit():
                    length = int(length)
                    if length < 1:
                        print(colors.red + 'password length MUST be positive integer', colors.reset)
                        print()
                        continue
                else:
                    print(colors.red + 'password length MUST be positive integer', colors.reset)
                    print()
                    continue
                try:
                    # we haven't check output_format!
                    password = generate_password(service_name, main_password, output_format, length)
                except Exception as error:
                    maybe_raise(error)
                    print()
                    continue
                service_names = maybe_add_service_name(service_name, password, service_names)

            print(colors.green + service_name + colors.reset)

            if args.output == 'stdout':
                print(colors.yellow + password + colors.reset)
            else:
                clipboard_buffer = pyperclip.paste()
                pyperclip.copy(password)
                print(colors.yellow + 'Password has been copied to clipboard' + colors.reset)
                if args.sleep > 0:
                    print(colors.white + 'waiting for {}s to remove password from clipboard'.format(args.sleep) + colors.reset)
                    sleep_time = args.sleep
                    while sleep_time != 0:
                        print(colors.grey + str(sleep_time) + colors.reset, end=' ', flush=True)
                        sleep(1)
                        sleep_time -= 1
                    print()
                    pyperclip.copy(clipboard_buffer)
            print()
            # Sounds like you have read the entire shit, f**k you don't judge me!
    except KeyboardInterrupt:
        print()
    except Exception as error:
        maybe_raise(error)
        exit(1)
