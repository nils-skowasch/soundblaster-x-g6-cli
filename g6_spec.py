from enum import Enum

from g6_util import read_payload_as_hex_lines


class StaticsEnum(Enum):
    PREFIX = 0
    INTERMEDIATE = 1


class RequestTypeEnum(Enum):
    DATA = 0
    COMMIT = 1


class AudioFeatureEnum(Enum):
    SURROUND = 0
    CRYSTALIZER = 1
    BASS = 2
    SMART_VOLUME = 3
    DIALOG_PLUS = 4


class AudioFeatureSpecialValueEnum(Enum):
    SMART_VOLUME_NIGHT = 0
    SMART_VOLUME_LOUD = 1


class AudioFeature:
    def __init__(self, toggle_hex, slider_hex):
        self.toggle_hex = toggle_hex
        self.slider_hex = slider_hex


class AudioFeatureExtended(AudioFeature):
    def __init__(self, toggle_hex, slider_hex, slider_special_hex, slider_special_enabled_value_hex,
                 slider_special_disabled_value_hex):
        super().__init__(toggle_hex, slider_hex)
        self.slider_special_hex = slider_special_hex
        self.slider_special_enabled_value_hex = slider_special_enabled_value_hex
        self.slider_special_disabled_value_hex = slider_special_disabled_value_hex


class Audio:
    def __init__(self, payload_number_values_hex_path):
        # define static hex values
        self.static_dict = {
            StaticsEnum.PREFIX: 0x5a,
            StaticsEnum.INTERMEDIATE: 0x0196
        }
        # define request type hex values
        self.request_type_dict = {
            RequestTypeEnum.DATA: 0x1207,
            RequestTypeEnum.COMMIT: 0x1103
        }
        # define audio feature hex values
        self.audio_feature_dict = {
            AudioFeatureEnum.SURROUND: AudioFeature(0x00, 0x01),
            AudioFeatureEnum.CRYSTALIZER: AudioFeature(0x07, 0x08),
            AudioFeatureEnum.BASS: AudioFeature(0x18, 0x19),
            AudioFeatureEnum.SMART_VOLUME: AudioFeatureExtended(0x04, 0x05, 0x06,
                                                                0x0000803f,
                                                                0x00000040),
            AudioFeatureEnum.DIALOG_PLUS: AudioFeature(0x02, 0x03)
        }
        # parse number hex values
        self.number_value_dict = {}
        hex_lines = read_payload_as_hex_lines(payload_number_values_hex_path)
        # check the file's number of lines
        expected_line_count = 202
        if not len(hex_lines) == expected_line_count:
            raise RuntimeError(
                f"The file {payload_number_values_hex_path} seems to be corrupted, since it does not contain the "
                f"expected {expected_line_count} lines! Aborting execution.")
        # read from every even line, which is a 'Data' line containing a number's value (from 0-100)
        expected_line_length = 128
        for i in range(0, len(hex_lines), 2):
            hex_line = hex_lines[i]
            # check hex_line length
            if len(hex_line) != expected_line_length:
                raise RuntimeError(f"The file {payload_number_values_hex_path} seems to be corrupted."
                                   f"Expected the hex_line '{hex_lines}' to have a length of {expected_line_length} "
                                   f"characters, but it had {len(hex_line)} characters!")
            # check hex_line containing Data request type ('1207')
            if not hex_line.__contains__(self.__to_hex_str(self.request_type_dict[RequestTypeEnum.DATA])):
                raise RuntimeError(f"The file {payload_number_values_hex_path} seems to be corrupted."
                                   f"The hex_line '{hex_lines}' does not contain the expected 'DATA' request type:"
                                   f" '{str(self.request_type_dict[RequestTypeEnum.DATA])}'!")
            self.number_value_dict[int(i / 2)] = int(hex_line[12:20], 16)

    def build_hex_lines_toggle(self, audio_feature_enum, enabled):
        """
        Build a list of 64 byte hex-line commands for the given AudioFeature's toggle.
        :param audio_feature_enum: the enum value of the AudioFeature to build the hex-line for
        :param enabled: the boolean value, whether to enable or disable the AudioFeature.
        :return: a list of hex-line commands, designated being sent to the G6.
        """
        if type(audio_feature_enum) is not AudioFeatureEnum:
            raise ValueError(f'Argument \'audio_feature_enum\' should be of type \'{type(AudioFeatureEnum)}\','
                             f' but was \'{type(audio_feature_enum)}\'!')
        if type(enabled) is not bool:
            raise ValueError(f'Argument \'enabled\' should be of type \'{type(bool)}\','
                             f' but was \'{type(enabled)}\'!')

        audio_feature_hex = self.audio_feature_dict[audio_feature_enum].toggle_hex
        value_hex = self.number_value_dict[100] if enabled else self.number_value_dict[0]

        return [
            self.__build_hex_line(RequestTypeEnum.DATA, audio_feature_hex, value_hex),
            self.__build_hex_line(RequestTypeEnum.COMMIT, audio_feature_hex, 0)
        ]

    def build_hex_lines_slider(self, audio_feature_enum, value):
        """
        Build a list of 64 byte hex-line commands for the given AudioFeature's slider value.
        :param audio_feature_enum: the enum value of the AudioFeature to build the hex-line for
        :param value: the integer value for the slider of the corresponding AudioFeature (0 - 100)
        :return: a list of hex-line commands, designated being sent to the G6.
        """
        if type(audio_feature_enum) is not AudioFeatureEnum:
            raise ValueError(f'Argument \'audio_feature_enum\' should be of type \'{type(AudioFeatureEnum)}\','
                             f' but was \'{type(audio_feature_enum)}\'!')
        if type(value) is not int:
            raise ValueError(f'Argument \'value\' should be of type \'{type(int)}\','
                             f' but was \'{type(value)}\'!')
        if value < 0 or value > 100:
            raise ValueError(f'Argument \'value\' should be between \'0\' and \'100\', but was \'{value}\'!')

        audio_feature_hex = self.audio_feature_dict[audio_feature_enum].slider_hex
        value_hex = self.number_value_dict[value]

        return [
            self.__build_hex_line(RequestTypeEnum.DATA, audio_feature_hex, value_hex),
            self.__build_hex_line(RequestTypeEnum.COMMIT, audio_feature_hex, 0)
        ]

    def build_hex_lines_slider_special(self, audio_feature_enum, audio_feature_special_value_enum):
        """
        Build a list of 64 byte hex-line commands for the given AudioFeature's slider special value.
        :param audio_feature_enum: the enum value of the AudioFeature to build the hex-line for
        :param audio_feature_special_value_enum: the value to set as AudioFeatureSpecialValueEnum enum value
        :return: a list of hex-line commands, designated being sent to the G6.
        """
        if type(audio_feature_enum) is not AudioFeatureEnum:
            raise ValueError(f'Argument \'audio_feature_enum\' should be of type \'{type(AudioFeatureEnum)}\','
                             f' but was \'{type(audio_feature_enum)}\'!')
        if type(audio_feature_special_value_enum) is not AudioFeatureSpecialValueEnum:
            raise ValueError(f'Argument \'audio_feature_special_value_enum\' should be of type '
                             f'\'{type(AudioFeatureSpecialValueEnum)}\','
                             f' but was \'{type(audio_feature_special_value_enum)}\'!')

        if audio_feature_enum is AudioFeatureEnum.SMART_VOLUME and \
                (audio_feature_special_value_enum is AudioFeatureSpecialValueEnum.SMART_VOLUME_NIGHT
                 or audio_feature_special_value_enum is AudioFeatureSpecialValueEnum.SMART_VOLUME_LOUD):
            audio_feature_hex = self.audio_feature_dict[audio_feature_enum].slider_special_hex
            value_hex = self.audio_feature_dict[audio_feature_enum].slider_special_enabled_value_hex \
                if audio_feature_special_value_enum is AudioFeatureSpecialValueEnum.SMART_VOLUME_LOUD \
                else self.audio_feature_dict[audio_feature_enum].slider_special_disabled_value_hex
        else:
            raise ValueError(f'Unexpected combination of audio_feature_enum \'{audio_feature_enum}\' and '
                             f'audio_feature_special_value_enum \'{audio_feature_special_value_enum}\'!')

        return [
            self.__build_hex_line(RequestTypeEnum.DATA, audio_feature_hex, value_hex),
            self.__build_hex_line(RequestTypeEnum.COMMIT, audio_feature_hex, 0)
        ]

    def __build_hex_line(self, request_type_enum, audio_feature_hex, value_hex):
        if type(request_type_enum) is not RequestTypeEnum:
            raise ValueError(f'Argument \'request_type_enum\' should be of type \'{type(RequestTypeEnum)}\','
                             f' but was \'{type(request_type_enum)}\'!')
        if type(audio_feature_hex) is not int:
            raise ValueError(f'Argument \'audio_feature_hex\' should be of type \'{type(int)}\','
                             f' but was \'{type(audio_feature_hex)}\'!')
        if type(value_hex) is not int:
            raise ValueError(f'Argument \'value_hex\' should be of type \'{type(int)}\','
                             f' but was \'{type(value_hex)}\'!')

        static_prefix = self.__to_hex_str(self.static_dict[StaticsEnum.PREFIX]).zfill(2)
        request_type = self.__to_hex_str(self.request_type_dict[request_type_enum]).zfill(4)
        static_intermediate = self.__to_hex_str(self.static_dict[StaticsEnum.INTERMEDIATE]).zfill(4)
        audio_feature = self.__to_hex_str(audio_feature_hex).zfill(2)
        value = self.__to_hex_str(value_hex).zfill(8)

        assembled = f'{static_prefix}{request_type}{static_intermediate}{audio_feature}{value}'
        assembled_len = len(assembled)
        if assembled_len != 20:
            raise RuntimeError(f'The assembled hex_line part should have 20 characters, but it'
                               f' had {assembled_len}: \'{assembled}\'!')

        hex_line = assembled + '0' * 108
        hex_line_len = len(hex_line)
        if hex_line_len != 128:
            raise RuntimeError(f'The assembled hex_line should have 128 characters, but it'
                               f' had {hex_line_len}: \'{hex_line}\'!')

        return hex_line

    @staticmethod
    def __to_hex_str(int_value):
        return format(int_value, 'x')
