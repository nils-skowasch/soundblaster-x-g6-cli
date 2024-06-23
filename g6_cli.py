import argparse
import os.path
import re
import tempfile
import hid

from g6_spec import Audio, AudioFeatureEnum, AudioFeatureSpecialValueEnum
from g6_util import read_payload_as_hex_lines

# G6 specific USB information
G6_VENDOR_ID = 0x041e
G6_PRODUCT_ID = 0x3256
# The G6 has four interface (2 Audio and 2 HDI), the endpoint of the fourth interface is used by SoundBlaster Connect.
# So will we, since data sent to the third interface is ignored by the device.
G6_INTERFACE = 4
# The name of the temporary file to remember the last toggle state in. If the file could not be found. The program
# lets the G6 to toggle to Speakers by default.
TOGGLE_STATE_TEMP_FILE_NAME = 'g6-cli-toggle-state'
TOGGLE_STATE_SPEAKERS = 'Speakers'
TOGGLE_STATE_HEADPHONES = 'Headphones'
# The payloads available to send to the G6
PAYLOAD_DIR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'payloads')
PAYLOAD_TOGGLE_TO_HEADPHONES_PATH = os.path.join(PAYLOAD_DIR_PATH, 'toggle-output-to-headphones.hex')
PAYLOAD_TOGGLE_TO_SPEAKERS_PATH = os.path.join(PAYLOAD_DIR_PATH, 'toggle-output-to-speakers.hex')
PAYLOAD_NUMBER_VALUES_PATH = os.path.join(PAYLOAD_DIR_PATH, '0-100.hex')
PAYLOAD_HEX_LINE_PATTERN = r'^[a-f0-9]{128}$'
# The udev rule to create in /etc/udev/rules.d/50-soundblaster-x-g6.rules
UDEV_RULE = r'SUBSYSTEM=="usb", ATTRS{idVendor}=="041e", ATTRS{idProduct}=="3256", TAG+="uaccess"'


def parse_cli_args():
    """
    Parse the CLI arguments using argparse.
    Prints the CLI help to console and raises an error, if the arguments are invalid.
    :return: the parsed cli args object
    """
    numbers = [i for i in range(0, 101)]
    enabled_disabled = ['Enabled', 'Disabled']

    parser = argparse.ArgumentParser(description='SoundBlaster X G6 CLI')
    #
    # Base options
    #
    # -- toggle-output
    parser.add_argument('--toggle-output', required=False, action='store_true',
                        help='Toggles the sound output between Speakers and Headphones')
    # --set-output
    parser.add_argument('--set-output', required=False, type=str,
                        choices=[TOGGLE_STATE_SPEAKERS, TOGGLE_STATE_HEADPHONES])
    # --dry-run
    parser.add_argument('--dry-run', required=False, action='store_true',
                        help='Used to verify the available hex_line files, without making '
                             'any calls against the G6 device.')
    #
    # Sound Effects
    #
    # --set-surround
    parser.add_argument('--set-surround', required=False, type=str, choices=enabled_disabled,
                        help='Enables or disables the Surround sound effect: [\'Enabled\', \'Disabled\']')
    parser.add_argument('--set-surround-value', required=False, type=int, choices=numbers,
                        help='Set the value for the Surround sound effect as integer: [0 .. 100].')
    # --set-crystalizer
    parser.add_argument('--set-crystalizer', required=False, type=str, choices=enabled_disabled,
                        help='Enables or disables the Crystalizer sound effect: [\'Enabled\', \'Disabled\']')
    parser.add_argument('--set-crystalizer-value', required=False, type=int, choices=numbers,
                        help='Set the value for the Crystalizer sound effect as integer: [0 .. 100].')
    # --set-bass
    parser.add_argument('--set-bass', required=False, type=str, choices=enabled_disabled,
                        help='Enables or disables the Bass sound effect: [\'Enabled\', \'Disabled\']')
    parser.add_argument('--set-bass-value', required=False, type=int, choices=numbers,
                        help='Set the value for the Bass sound effect as integer: [0 .. 100].')
    # --set-smart-volume
    parser.add_argument('--set-smart-volume', required=False, type=str, choices=enabled_disabled,
                        help='Enables or disables the Smart-Volume sound effect: [\'Enabled\', \'Disabled\']')
    parser.add_argument('--set-smart-volume-value', required=False, type=int, choices=numbers,
                        help='Set the value for the Smart-Volume sound effect as value: [0 .. 100].')
    parser.add_argument('--set-smart-volume-special-value', required=False, type=str, choices=['Night', 'Loud'],
                        help='Set the value for the Smart-Volume sound effect as string: \'Night\', \'Loud\'. '
                             'Supersedes the value from \'--set-smart-volume-value\'!')
    # --set-dialog-plus
    parser.add_argument('--set-dialog-plus', required=False, type=str, choices=enabled_disabled,
                        help='Enables or disables the Dialog-Plus sound effect: [\'Enabled\', \'Disabled\']')
    parser.add_argument('--set-dialog-plus-value', required=False, type=int, choices=numbers,
                        help='Set the value for the Dialog-Plus sound effect as integer: : [0 .. 100].')

    # parse args and verify
    args = parser.parse_args()
    if args.toggle_output is False \
            and args.set_output is None \
            and args.set_surround is None \
            and args.set_surround_value is None \
            and args.set_crystalizer is None \
            and args.set_crystalizer_value is None \
            and args.set_bass is None \
            and args.set_bass_value is None \
            and args.set_smart_volume is None \
            and args.set_smart_volume_value is None \
            and args.set_smart_volume_special_value is None \
            and args.set_dialog_plus is None \
            and args.set_dialog_plus_value is None:
        message = 'No meaningful argument has been specified!'
        print(message)
        parser.print_help()
        raise ValueError(message)
    elif args.toggle_output is True and args.set_output is not None:
        message = 'Only one of the following CLI arguments may be specified: \'--toggle-output', '--set-output\'!'
        print(message)
        parser.print_help()
        raise ValueError(message)

    return args


def detect_device():
    """
    Tries to detect the SoundBlaster X G6 device and returns the device path to it.

    From all connected USB HID devices, we filter all devices which do not match the desired vendor_id and product_id.
    Since we know, that we have to communicate with USB-Interface 4, we also filter all other interfaces of the device.
    This approach is required, because the G6's endpoint of the third HID interface ignores any data transmitted to
    it. We have to use the endpoint of the fourth interface!

    If the device itself or the fourth interface could not be found, an IOError is risen to let the program terminate.

    Example for a device_path: "b'5-2.1:1.4'"
    - Bus 5
    - Port 2 (USB-Hub at Bus)
    - Port 1 (G6 at Hub)
    - bConfigurationValue 1
    - Interface 4

    A tree output of all connected USB devices can be generated with the command `lsusb -t`.
    :return: The unique device_path to the G6.
    """
    device_found = False
    for device_dict in hid.enumerate():
        if device_dict['vendor_id'] == G6_VENDOR_ID and device_dict['product_id']:
            device_found = True
            if G6_PRODUCT_ID and device_dict['interface_number'] == G6_INTERFACE:
                device_path = device_dict['path']
                print(f'Device detected at path: {device_path}')
                return device_path
    if device_found:
        raise IOError(
            f"The SoundBlaster X G6 device could be found having vendor_id='{G6_VENDOR_ID:#x}' and product_id"
            f"='{G6_PRODUCT_ID:#x}'. But the required fourth HDI interface does not seem to be available. "
            f"Something is wrong here, and thus, the program execution is terminated!")
    else:
        raise IOError(
            f"No SoundBlaster X G6 device could be found having vendor_id='{G6_VENDOR_ID:#x}' and "
            f"product_id='{G6_PRODUCT_ID:#x}'. Is the device connected to your system? Are you allowed to access the "
            f"device (missing udev-rules in linux)?")


def list_all_devices():
    """
    Simply prints information of all detected usb devices to the console
    """
    for device_dict in hid.enumerate():
        keys = list(device_dict.keys())
        keys.sort()
        for key in keys:
            print("%s : %s" % (key, device_dict[key]))
        print()


def read_toggle_state_file(toggle_state_file_path):
    """
    Read the toggle state from the temporary file to determine the state from previous runs.
    :param toggle_state_file_path: The path to the file, where the last toggle state has been remembered in.
    :return: The content of the file. Should be either 'Speakers' or 'Headphones'.
    """
    with open(toggle_state_file_path, 'r') as file:
        return file.read()


def write_toggle_state_file(toggle_state_file_path, toggle_state_value):
    """
    Write the currently used toggle_state to the temporary file for next runs.
    :param toggle_state_file_path: The path to the file for remembering the last set toggle state.
    :param toggle_state_value: The toggle state to write to the file. Should be either 'Speakers' or 'Headphones'.
    """
    with open(toggle_state_file_path, 'w') as file:
        file.write(str(toggle_state_value))


def determine_toggle_state():
    """
    Reads the last used toggle_state value from the temporary file to determine the next value.
    If the temporary file does not exist, 'Speakers' is used by default.
    :return: The just set and now active toggle state value.
    """
    toggle_state_file_path = os.path.join(tempfile.gettempdir(), TOGGLE_STATE_TEMP_FILE_NAME)
    # determine toggle state from temporary file or use SPEAKERS by default
    if os.path.exists(toggle_state_file_path):
        current_toggle_state = read_toggle_state_file(toggle_state_file_path)
        next_toggle_state = TOGGLE_STATE_SPEAKERS \
            if current_toggle_state == TOGGLE_STATE_HEADPHONES \
            else TOGGLE_STATE_HEADPHONES
        print(
            f'Toggle from '
            f'{current_toggle_state} -> {next_toggle_state}')
    else:
        next_toggle_state = TOGGLE_STATE_SPEAKERS
        print(f'Toggle to {next_toggle_state}')
    # write next toggle state to temporary file
    write_toggle_state_file(toggle_state_file_path, next_toggle_state)
    # return the next toggle state to send it to the G6
    return next_toggle_state


def device_toggle_output(device_path, dry_run):
    """
    Toggles the device's output. Either Speakers -> Headphones or Headphones -> Speakers.
    :param device_path: The detected usb device path for the G6.
    :param dry_run: whether to simulate communication with the device for program testing purposes.
                    If set to true, no data is sent to the G6!
    """
    # determine next toggle state
    toggle_state = determine_toggle_state()
    # determine payload to load
    payload_file_path = PAYLOAD_TOGGLE_TO_SPEAKERS_PATH \
        if toggle_state == TOGGLE_STATE_HEADPHONES \
        else PAYLOAD_TOGGLE_TO_HEADPHONES_PATH
    # read payload from file
    payload_hex_lines = read_payload_as_hex_lines(payload_file_path)
    # send the payload to the device
    print(f'About to send payload to device: {payload_file_path}')
    send_to_device(device_path, payload_hex_lines, dry_run)


def device_set_output(device_path, toggle_state, dry_run):
    """
    Set a specific device output. Either 'Speakers' or 'Headphones'
    :param device_path: The detected usb device path for the G6.
    :param toggle_state: the toggle_state value to set the G6's output to. Should be either 'Speakers' or 'Headphones'.
    :param dry_run: whether to simulate communication with the device for program testing purposes.
                    If set to true, no data is sent to the G6!
    """
    # determine payload to load
    if toggle_state == TOGGLE_STATE_SPEAKERS:
        payload_file_path = PAYLOAD_TOGGLE_TO_SPEAKERS_PATH
    elif toggle_state == TOGGLE_STATE_HEADPHONES:
        payload_file_path = PAYLOAD_TOGGLE_TO_HEADPHONES_PATH
    else:
        raise ValueError(
            f'The given toggle_state must either be {TOGGLE_STATE_SPEAKERS} or {TOGGLE_STATE_HEADPHONES}, '
            f'but was {toggle_state}!')
    # read payload from file
    payload_hex_lines = read_payload_as_hex_lines(payload_file_path)
    # send the payload to the device
    print(f'About to send payload to device: {payload_file_path}')
    send_to_device(device_path, payload_hex_lines, dry_run)


def device_set_audio_effects(device_path, audio, args):
    """
    Sends all as CLI args given audio effects to the device.
    :param device_path: The detected usb device path for the G6.
    :param audio: An instance of the class Audio from g6_spec.py
    :param args: the CLI arguments, recently parsed by argparse in parse_cli_args()
    """
    # surround
    if args.set_surround is not None:
        hex_lines = audio.build_hex_lines_toggle(AudioFeatureEnum.SURROUND, to_bool(args.set_surround))
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_surround_value is not None:
        hex_lines = audio.build_hex_lines_slider(AudioFeatureEnum.SURROUND, args.set_surround_value)
        send_to_device(device_path, hex_lines, args.dry_run)
    # crystalizer
    if args.set_crystalizer is not None:
        hex_lines = audio.build_hex_lines_toggle(AudioFeatureEnum.CRYSTALIZER, to_bool(args.set_crystalizer))
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_crystalizer_value is not None:
        hex_lines = audio.build_hex_lines_slider(AudioFeatureEnum.CRYSTALIZER, args.set_crystalizer_value)
        send_to_device(device_path, hex_lines, args.dry_run)
    # bass
    if args.set_bass is not None:
        hex_lines = audio.build_hex_lines_toggle(AudioFeatureEnum.BASS, to_bool(args.set_bass))
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_bass_value is not None:
        hex_lines = audio.build_hex_lines_slider(AudioFeatureEnum.BASS, args.set_bass_value)
        send_to_device(device_path, hex_lines, args.dry_run)
    # smart-volume
    if args.set_smart_volume is not None:
        hex_lines = audio.build_hex_lines_toggle(AudioFeatureEnum.SMART_VOLUME, to_bool(args.set_smart_volume))
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_smart_volume_value is not None:
        hex_lines = audio.build_hex_lines_slider(AudioFeatureEnum.SMART_VOLUME, args.set_smart_volume_value)
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_smart_volume_special_value is not None:
        smart_volume_special_value = None
        if args.set_smart_volume_special_value == 'Night':
            smart_volume_special_value = AudioFeatureSpecialValueEnum.SMART_VOLUME_NIGHT
        elif args.set_smart_volume_special_value == 'Loud':
            smart_volume_special_value = AudioFeatureSpecialValueEnum.SMART_VOLUME_LOUD
        else:
            raise ValueError(f'Expected one of the following values for --smart-volume-special-value: '
                             f'[\'Night\', \'Loud\'], but was \'{args.set_smart_volume_special_value}\'!')
        hex_lines = audio.build_hex_lines_slider_special(AudioFeatureEnum.SMART_VOLUME, smart_volume_special_value)
        send_to_device(device_path, hex_lines, args.dry_run)
    # dialog-plus
    if args.set_dialog_plus is not None:
        hex_lines = audio.build_hex_lines_toggle(AudioFeatureEnum.DIALOG_PLUS, to_bool(args.set_dialog_plus))
        send_to_device(device_path, hex_lines, args.dry_run)
    if args.set_dialog_plus_value is not None:
        hex_lines = audio.build_hex_lines_slider(AudioFeatureEnum.DIALOG_PLUS, args.set_dialog_plus_value)
        send_to_device(device_path, hex_lines, args.dry_run)


def to_bool(enabled_disabled):
    """
    Converts the given string to a boolean value or raises a ValueError, if an unexpected value is supplied.
    :param enabled_disabled: 'Enabled' -> true; 'Disabled' -> false
    :return: the converted boolean value
    """
    if enabled_disabled == 'Enabled':
        return True
    elif enabled_disabled == 'Disabled':
        return False
    else:
        raise ValueError(f'Argument \'enabled_disabled\' has an unexpected value! Expected either \'Enabled\' or'
                         f' \'Disabled\', but was \'{enabled_disabled}\'!')


def send_to_device(device_path, payload_hex_lines, dry_run):
    """
    Send the payload_hex_lines to an endpoint from the usb device, identified by the device_path.
    :param device_path: The detected usb device path for the G6.
    :param payload_hex_lines: A list of hexlines (raw usb payload) to send to the G6.
                              Each line must be 128 characters long (64 bytes).
    :param dry_run: whether to simulate communication with the device for program testing purposes.
                    If set to true, no data is sent to the G6!
    """
    try:
        print(f"Opening the device '{device_path}' ...")
        h = hid.device()
        h.open_path(device_path)
        print(f"Opening the device '{device_path}': ok.")

        print(f"Manufacturer: '{h.get_manufacturer_string()}'")
        print(f"Product: '{h.get_product_string()}'")
        print(f"Serial No: '{h.get_serial_number_string()}'")

        # enable non-blocking mode
        h.set_nonblocking(1)

        # Validate all hex_lines
        regex_pattern = re.compile(PAYLOAD_HEX_LINE_PATTERN)
        for hex_line in payload_hex_lines:
            if not regex_pattern.fullmatch(hex_line):
                raise ValueError(
                    f"The following hex_line is part of the payload, but it did not match the expected regex pattern! "
                    f"Pattern: '{PAYLOAD_HEX_LINE_PATTERN}'; "
                    f"Hex-Line: '{hex_line}'")

        for hex_line in payload_hex_lines:
            # Prepend an additional zero byte as report_id to the hex_line. Otherwise, the first byte from the actual
            # 64 byte payload is cut off, since it is interpreted as report_id and thus, not sent to the device.
            hex_line = '00' + hex_line

            # Convert the hex string to a list of integers
            integer_list = [int(hex_line[i:i + 2], 16) for i in range(0, len(hex_line), 2)]

            # send the data to the device
            print("Sending data to G6 ...")
            print(hex_line)
            if dry_run:
                print("This is a dry run. No data has been sent!")
            else:
                h.write(integer_list)
            print("Sending data to G6: ok.")

            # read back the response
            if not dry_run:
                print("Read the response:")
                while True:
                    d = h.read(64)
                    if d:
                        print(d)
                    else:
                        break

        print("Closing the device")
        h.close()

    except IOError as ex:
        print(f'Unable to open a connection to the device by path: {device_path}')
        print(ex)
        print('\nAre the udev rules set and used by the kernel?')
        print('Create a udev-rule file at `/etc/udev/rules.d/50-soundblaster-x-g6.rules` with the following content:')
        print(UDEV_RULE)
        print('\nIf the file already exists, it might not be used by the kernel. Try to reload the configuration with:')
        print("`sudo udevadm trigger`")


def main():
    args = parse_cli_args()
    device_path = detect_device()
    audio = Audio(PAYLOAD_NUMBER_VALUES_PATH)

    # handle device output
    if args.toggle_output:
        device_toggle_output(device_path, args.dry_run)
    elif args.set_output is not None:
        device_set_output(device_path, args.set_output, args.dry_run)

    # handle audio effects
    device_set_audio_effects(device_path, audio, args)


if __name__ == "__main__":
    main()
