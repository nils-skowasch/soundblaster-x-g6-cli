# USB protocol

This chapter contains some notes about the USB protocol.

**Note that most of the information has been generated
using ChatGPT and is not verified by any literature!**

## USB Descriptors

In a USB device's descriptor response, the association between an endpoint and an interface is explicitly defined within
the Configuration Descriptor. The Configuration Descriptor contains one or more Interface Descriptors, and each
Interface Descriptor can include one or more Endpoint Descriptors. This hierarchy is used to describe how endpoints are
linked to interfaces.

### Configuration Descriptor

The Configuration Descriptor provides an overview of the entire configuration, including the number of interfaces it
contains.

```
Configuration Descriptor:
  bLength                 9
  bDescriptorType         2
  wTotalLength           34
  bNumInterfaces          1
  bConfigurationValue     1
  iConfiguration          0
  bmAttributes         0x80
  MaxPower               50
```

### Interface Descriptor

Each Interface Descriptor provides information about a specific interface, including the number of endpoints associated
with that interface.

In the context of USB (Universal Serial Bus), `bDescriptorType` is a field within a descriptor that specifies the type
of descriptor being used. Descriptors are data structures that provide information about the USB device, its
configuration, interface, and endpoints. Each descriptor type is assigned a specific numerical value.

When `bDescriptorType` has a value of `4`, it indicates an **Interface Descriptor**. The Interface Descriptor provides
information about a specific interface within a configuration of the USB device. It includes details such as the number
of endpoints used by the interface, the class, subclass, and protocol code, and the string descriptor describing the
interface.

Here’s a breakdown of the fields within an Interface Descriptor:

- **bLength**: Size of this descriptor in bytes.
- **bDescriptorType**: Descriptor type, which is `4` for an Interface Descriptor.
- **bInterfaceNumber**: Number identifying this interface.
- **bAlternateSetting**: Value used to select an alternate setting for this interface.
- **bNumEndpoints**: Number of endpoints used by this interface (excluding the default control endpoint).
- **bInterfaceClass**: Class code (assigned by the USB-IF).
- **bInterfaceSubClass**: Subclass code (assigned by the USB-IF).
- **bInterfaceProtocol**: Protocol code (assigned by the USB-IF).
- **iInterface**: Index of string descriptor describing this interface.

An example of an Interface Descriptor might look like this in a USB device descriptor table:

```
Interface Descriptor:
  bLength                9
  bDescriptorType        4
  bInterfaceNumber       0
  bAlternateSetting      0
  bNumEndpoints          1
  bInterfaceClass        3  Human Interface Device
  bInterfaceSubClass     1  Boot Interface Subclass
  bInterfaceProtocol     1  Keyboard
  iInterface             0
```

This example describes a Human Interface Device (HID) interface that uses one endpoint, belongs to the Boot Interface
Subclass, and follows the Keyboard protocol.

Understanding the value of `bDescriptorType` and its associated descriptor is crucial for correctly interpreting the
capabilities and structure of a USB device.

### Endpoint Descriptor

Each Endpoint Descriptor provides information about a specific endpoint, including its address and attributes.

When `bDescriptorType` has a value of `5` in a USB descriptor, it refers to an **Endpoint Descriptor**. Endpoint
Descriptors provide information about the endpoints used by a USB device interface. Each endpoint, other than the
default control endpoint (endpoint 0), must have an associated Endpoint Descriptor.

Here’s a breakdown of the fields within an Endpoint Descriptor:

- **bLength**: Size of this descriptor in bytes.
- **bDescriptorType**: Descriptor type, which is `5` for an Endpoint Descriptor.
- **bEndpointAddress**: The address of the endpoint on the USB device. This field specifies the endpoint number and
  direction (IN or OUT).
- **bmAttributes**: Attributes that specify the endpoint’s transfer type (Control, Isochronous, Bulk, or Interrupt) and
  other characteristics.
- **wMaxPacketSize**: The maximum packet size this endpoint is capable of sending or receiving.
- **bInterval**: Interval for polling the endpoint for data transfers, in milliseconds (relevant for interrupt and
  isochronous endpoints).

An example of an Endpoint Descriptor might look like this:

```
Endpoint Descriptor:
  bLength              7
  bDescriptorType      5
  bEndpointAddress     81h  (EP 1 IN)
  bmAttributes         03h  (Interrupt)
  wMaxPacketSize       0008h  (8 bytes)
  bInterval            0Ah  (10 ms)
```

#### Detailed Explanation of Fields:

1. **bLength (1 byte)**:
    - The size of the descriptor in bytes. For an Endpoint Descriptor, this is typically 7 bytes.

2. **bDescriptorType (1 byte)**:
    - The type of descriptor. For an Endpoint Descriptor, this value is `5`.

3. **bEndpointAddress (1 byte)**:
    - The address of the endpoint. The most significant bit (bit 7) indicates the direction (0 for OUT, 1 for IN). The
      remaining bits (bits 0-3) specify the endpoint number.

4. **bmAttributes (1 byte)**:
    - Attributes of the endpoint. The lower two bits specify the transfer type (00 = Control, 01 = Isochronous, 10 =
      Bulk, 11 = Interrupt). The rest of the bits may specify additional characteristics depending on the transfer type.

5. **wMaxPacketSize (2 bytes)**:
    - The maximum packet size that the endpoint can handle. This value is expressed in bytes and may include additional
      information about the number of transactions per microframe for high-speed endpoints.

6. **bInterval (1 byte)**:
    - The polling interval for the endpoint in milliseconds. This field is mainly relevant for interrupt and isochronous
      endpoints, indicating how often the endpoint should be polled for data transfers.

#### Example Breakdown:

```
Endpoint Descriptor:
  bLength              7                 // Descriptor size in bytes
  bDescriptorType      5                 // Endpoint Descriptor type
  bEndpointAddress     81h  (EP 1 IN)    // Endpoint 1, IN direction
  bmAttributes         03h  (Interrupt)  // Interrupt transfer type
  wMaxPacketSize       0008h  (8 bytes)  // Max packet size is 8 bytes
  bInterval            0Ah  (10 ms)      // Polling interval is 10 ms
```

This example describes an interrupt IN endpoint (endpoint 1) with a maximum packet size of 8 bytes and a polling
interval of 10 milliseconds.

## USB Interface classes

In the USB specification, the `bInterfaceClass` field in the Interface Descriptor indicates the class of the interface.
USB defines several standard interface classes, each serving different purposes. Here are some of the most
common `bInterfaceClass` values along with their descriptions:

1. **Audio (Class Code 01h)**:
    - This class is used for audio devices such as microphones, speakers, and audio interfaces.

2. **Communication and CDC Control (Class Code 02h)**:
    - This class includes devices such as modems, Ethernet adapters, and serial ports.

3. **Human Interface Device (HID) (Class Code 03h)**:
    - HID devices include keyboards, mice, game controllers, and other human interface devices.

4. **Physical Interface Device (PID) (Class Code 05h)**:
    - PID devices are used for physical input devices like joysticks, knobs, and buttons.

5. **Image (Class Code 06h)**:
    - This class includes imaging devices such as cameras and scanners.

6. **Printer (Class Code 07h)**:
    - Printers and printing-related devices belong to this class.

7. **Mass Storage (Class Code 08h)**:
    - Mass storage devices include USB flash drives, external hard drives, and memory card readers.

8. **Hub (Class Code 09h)**:
    - Hubs are devices that provide additional USB ports for connecting multiple devices.

9. **CDC-Data (Class Code 0Ah)**:
    - This class is used for communication devices that transfer data, such as Ethernet adapters.

10. **Smart Card (Class Code 0Bh)**:
    - Smart card readers and related devices are classified under this class.

11. **Content Security (Class Code 0Dh)**:
    - Devices related to content protection and security belong to this class.

12. **Video (Class Code 0Eh)**:
    - Video devices such as webcams and video capture devices fall under this class.

13. **Personal Healthcare (Class Code 0Fh)**:
    - Devices related to personal healthcare and fitness monitoring are classified under this class.

14. **Diagnostic Device (Class Code DC, Subclass FEh)**:
    - Diagnostic devices used for testing and debugging USB communications.

These are just some of the standard USB interface classes defined by the USB specification. There are additional
vendor-specific and proprietary classes as well. Each class defines a set of protocols and specifications that devices
must adhere to for interoperability.

## USB data transfer types

USB supports four main types of data transfers, each tailored for specific purposes and with distinct characteristics.
These transfer types are:

1. **Control Transfers**:
    - **Purpose**: Control transfers are used for device configuration, enumeration, and control operations.
    - **Characteristics**:
        - Low speed (1.5 Mbps), full speed (12 Mbps), or high speed (480 Mbps).
        - Guaranteed delivery with error checking and retry mechanisms.
        - Bidirectional communication.
        - Limited bandwidth allocation.
    - **Usage**: Used for device initialization, configuration changes, and standard device requests (such as getting
      device descriptors or setting device configuration).

2. **Bulk Transfers**:
    - **Purpose**: Bulk transfers are used for large, non-time-sensitive data transfers.
    - **Characteristics**:
        - Typically used in high-speed and full-speed USB.
        - Reliability ensured through error detection and retransmission (in USB 2.0).
        - Not time-sensitive; designed for large data transfers that can tolerate delays.
    - **Usage**: Commonly used for transferring large amounts of data like file transfers, printing, or reading/writing
      from storage devices.

3. **Interrupt Transfers**:
    - **Purpose**: Interrupt transfers are used for low-volume, time-sensitive data transfers with bounded latency
      requirements.
    - **Characteristics**:
        - Low or full-speed USB.
        - Guaranteed maximum latency for each transfer.
        - Relatively low bandwidth allocation.
    - **Usage**: Suitable for time-sensitive data such as human interface devices (HID) like keyboards, mice, and game
      controllers, where low latency is crucial.

4. **Isochronous Transfers**:
    - **Purpose**: Isochronous transfers are used for streaming data with a fixed, guaranteed bandwidth and timing
      requirements.
    - **Characteristics**:
        - Continuous data streaming without error recovery.
        - No guaranteed delivery or error checking.
        - Used in real-time applications where maintaining a consistent data flow is more critical than ensuring
          error-free delivery.
    - **Usage**: Used for audio and video streaming, where maintaining a continuous flow of data is more important than
      ensuring every single piece of data arrives intact.

### Summary:

- **Control Transfers**: Used for configuration and control operations.
- **Bulk Transfers**: Suitable for large, non-time-sensitive data transfers.
- **Interrupt Transfers**: Ideal for low-volume, time-sensitive data transfers.
- **Isochronous Transfers**: Designed for streaming data with fixed bandwidth and timing requirements.

Each transfer type offers unique advantages and is chosen based on the specific requirements of the USB device and its
intended use case.