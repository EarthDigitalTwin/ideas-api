#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the California Institute of
#  Technology.  This software is subject to U.S. export control laws and regulations
#  and has been classified as EAR99.  By accepting this software, the user agrees to
#  comply with all applicable U.S. export laws and regulations.  User has the
#  responsibility to obtain export licenses, or other export authority as may be
#  required before exporting such information to foreign countries or providing
#  access to foreign persons.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datetime import datetime, timezone, timedelta


class TimeUtils:
    def __init__(self):
        self.__time_obj = datetime.utcnow()

    def parse_from_str(self, timestamp_str: str, fmt='%Y-%m-%dT%H:%M:%S%z', in_ms=False):
        self.__time_obj = datetime.strptime(timestamp_str, fmt)
        return self

    def parse_from_unix(self, unix_timestamp, in_ms=False):
        converting_timestamp = unix_timestamp / 1000 if in_ms is True else unix_timestamp
        self.__time_obj = datetime.fromtimestamp(converting_timestamp, timezone(timedelta(0, 0, 0, 0)))
        return self

    def get_datetime_obj(self):
        return self.__time_obj

    def get_datetime_unix(self, in_ms=False):
        return int(self.__time_obj.timestamp()) if not in_ms else int(self.__time_obj.timestamp() * 1000)

    def get_datetime_str(self, fmt='%Y-%m-%dT%H:%M:%S %z', in_ms=True):
        return self.__time_obj.strftime(fmt).replace('0000', '00:00')

    @staticmethod
    def get_current_time(doy_format=False, include_time=True, include_fraction=True):
        output_format = '%Y-%j' if doy_format is True else '%Y-%m-%d'
        if include_time:
            output_format = '{}T%H:%M:%S'.format(output_format)
            if include_fraction:
                output_format = '{}.%f'.format(output_format)
        # output_format = f'{output_format}%z'
        return datetime.utcnow().strftime(output_format)

    @staticmethod
    def get_time_obj(unix_timestamp, in_ms=True):
        converting_timestamp = unix_timestamp / 1000 if in_ms is True else unix_timestamp
        dt_obj = datetime.fromtimestamp(converting_timestamp, timezone(timedelta(0, 0, 0, 0)))
        return dt_obj

    @staticmethod
    def get_unix_time(timestamp_str: str, fmt='%Y-%m-%dT%H:%M:%S%z', in_ms=False):
        unix_timestamp = datetime.strptime(timestamp_str, fmt).timestamp()
        unix_timestamp = int(unix_timestamp) if not in_ms else int(unix_timestamp * 1000)
        return unix_timestamp

    @staticmethod
    def get_time_str(unix_timestamp, fmt='%Y-%m-%dT%H:%M:%S %z', in_ms=True):
        converting_timestamp = unix_timestamp / 1000 if in_ms is True else unix_timestamp
        dt_obj = datetime.fromtimestamp(converting_timestamp, timezone(timedelta(0, 0, 0, 0)))
        return dt_obj.strftime(fmt).replace('0000', '00:00')
