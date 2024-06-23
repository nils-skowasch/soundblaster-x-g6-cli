# SoundBlaster X G6 CLI

This project makes use of the [hidapi](https://github.com/trezor/cython-hidapi) library and thus transitively from
[libusb](https://github.com/libusb/libusb) to provide a CLI to control
the [SoundBlaster X G6](https://de.creative.com/p/sound-blaster/sound-blasterx-g6) device from command line. This empowers the people to control the G6 in Linux.

## Important Disclaimer

I developed this CLI to the best of my belief and I use it myself to control my G6, and it works fine for me.
I read pretty often, that you are able to damage or brick a USB device, if you send faulty data to it.

That's why I want point out, that you **USE THIS CLI AT YOUR OWN RISK**! I am not responsible for any damages on your
system or your device!

## Firmware version

This software is tested with a G6 having the **Firmware version:** `2.1.201208.1030`.

Make sure, that you have the same version, since I do not know whether the USB specification may differ between the 
versions. You are able to update your Firmware with 
[SoundBlaster Command](https://support.creative.com/Products/ProductDetails.aspx?prodID=21383&prodName=Sound%20Blaster)
 in Windows by using a [QEMU/KVM VM](https://virt-manager.org/) and the USB Redirection feature.

## Installation

Select a directory of your choice and clone the repository into it:

```shell
cd $HOME
git clone <repository-url>
```

Install Python3. The application has been tested with **Python3.10** (LinuxMint 21.3) and **Python3.12** (Windows 10):

```shell
sudo apt-get install Python3.10
```

This should create the directory `~/soundblaster-x-g6-cli`, containing all files.

The directory `~/soundblaster-x-g6-cli/shell` contains ready to use shell scripts to toggle or set the device output
of the SoundBlaster X G6. Just set the required file permissions and you should be good to go:

```shell
sudo chmod 0544 /home/<your-username>/soundblaster-x-g6-cli/shell/*
```

Create a virtual environment and download the dependencies using pip:

```shell
# create virtual environment 'venv'
cd /home/<your-username>/soundblaster-x-g6-cli/
python -m venv venv

# install virtualenv package (if required) and activate 'venv'
pip install virtualenv
virtualenv venv
source venv/bin/activate

# install dependencies into 'venv'
pip install -r requirements.txt
```

### Linux: Create udev-rule

In `/etc/udev/rules.d/` create a rule file as root (e.q. with name `50-soundblaster-x-g6.rules`) having the
following content:

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="041e", ATTRS{idProduct}=="3256", TAG+="uaccess"
```

This allows you (and the application) to access the USB device directly and is mandatory for the application to being 
able to send data to the device.

Apply the udev rules by issuing:
```shell
# Reload udev rules:
sudo udevadm trigger
```

### Linux: Install libusb1

The following libusb packages are required:

```txt
libusb-1.0-0-dev/jammy-updates,now 2:1.0.25-1ubuntu2 amd64 [installed]
libusb-1.0-0/jammy-updates,now 2:1.0.25-1ubuntu2 amd64 [installed]
```

### Windows: Add libusb-1.0.dll to %PATH%

Download the package [libusb](https://pypi.org/project/libusb/#files) from Pypi (version `1.0.27`) and add the 
following DLL file to your `%PATH%` variable:
`/libusb-1.0.27/src/libusb/_platform/_windows/x64/libusb-1.0.dll`

This is required to let the application use libusb in the backend.

### Conclusion

The shell scripts in `/home/<your-username>/soundblaster-x-g6-cli/shell/` should now be usable and the installation 
is complete.

## CLI usage

```shell
usage: g6_cli.py [-h] [--toggle-output] [--set-output {Speakers,Headphones}]
                 [--dry-run] [--set-surround {Enabled,Disabled}]
                 [--set-surround-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}]
                 [--set-crystalizer {Enabled,Disabled}]
                 [--set-crystalizer-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}]
                 [--set-bass {Enabled,Disabled}]
                 [--set-bass-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}]
                 [--set-smart-volume {Enabled,Disabled}]
                 [--set-smart-volume-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}]
                 [--set-smart-volume-special-value {Night,Loud}]
                 [--set-dialog-plus {Enabled,Disabled}]
                 [--set-dialog-plus-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}]

SoundBlaster X G6 CLI

options:
  -h, --help            show this help message and exit
  --toggle-output       Toggles the sound output between Speakers and
                        Headphones
  --set-output {Speakers,Headphones}
  --dry-run             Used to verify the available hex_line files, without
                        making any calls against the G6 device.
  --set-surround {Enabled,Disabled}
                        Enables or disables the Surround sound effect:
                        ['Enabled', 'Disabled']
  --set-surround-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}
                        Set the value for the Surround sound effect as
                        integer: [0 .. 100].
  --set-crystalizer {Enabled,Disabled}
                        Enables or disables the Crystalizer sound effect:
                        ['Enabled', 'Disabled']
  --set-crystalizer-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}
                        Set the value for the Crystalizer sound effect as
                        integer: [0 .. 100].
  --set-bass {Enabled,Disabled}
                        Enables or disables the Bass sound effect: ['Enabled',
                        'Disabled']
  --set-bass-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}
                        Set the value for the Bass sound effect as integer: [0
                        .. 100].
  --set-smart-volume {Enabled,Disabled}
                        Enables or disables the Smart-Volume sound effect:
                        ['Enabled', 'Disabled']
  --set-smart-volume-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}
                        Set the value for the Smart-Volume sound effect as
                        value: [0 .. 100].
  --set-smart-volume-special-value {Night,Loud}
                        Set the value for the Smart-Volume sound effect as
                        string: 'Night', 'Loud'. Supersedes the value from '--
                        set-smart-volume-value'!
  --set-dialog-plus {Enabled,Disabled}
                        Enables or disables the Dialog-Plus sound effect:
                        ['Enabled', 'Disabled']
  --set-dialog-plus-value {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100}
                        Set the value for the Dialog-Plus sound effect as
                        integer: : [0 .. 100].
```

# G6 USB specification

I reverse engineered the USB specification by recording the USB communication using 
[Wireshark USBPCAP](https://wiki.wireshark.org/CaptureSetup/USB) and making conclusions of the HEX codes being 
transmitted from 
[SoundBlaster Command](https://support.creative.com/Products/ProductDetails.aspx?prodID=21383&prodName=Sound%20Blaster) 
to the device:

See: [usb-spec.txt](./doc/usb-spec.txt)

# USB protocol

The following file contains some basic information about the USB protocol:

See: [usb-protocol.md](./doc/usb-protocol.md)
