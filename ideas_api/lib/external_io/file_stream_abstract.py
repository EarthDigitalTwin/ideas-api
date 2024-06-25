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

from abc import ABC, abstractmethod
from typing import Any, Union, Callable


class FileStreamAbstract(ABC):
    @abstractmethod
    def has_file(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def get_all_versions(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def get_modified_date(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def upload_parts_begin(self, base_path: str, relative_path: str, tags: dict = {}):
        return

    @abstractmethod
    def upload_part_x(self, body: bytes):
        return

    @abstractmethod
    def upload_parts_end(self):
        return

    @abstractmethod
    def get_size(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def get_version(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def get_stream(self, base_path, relative_path):
        return

    @abstractmethod
    def read_text_file(self, base_path: str, relative_path: str):
        return

    @abstractmethod
    def delete(self, base_path: str, relative_path: str, version_id: str = None):
        return

    @abstractmethod
    def download(self, base_path, relative_path, abs_folder_path, local_filename=None) -> str:
        """

        :param base_path:
        :param relative_path:
        :param abs_folder_path:
        :param local_filename:
        :return: str - downloaded file path
        """
        return ''

    @abstractmethod
    def split_url(self, absolute_path: str) -> tuple:
        """

        :param absolute_path:
        :return: tuple - (bucket, path)
        """
        return '', ''

    @abstractmethod
    def to_url(self, base_path: str, relative_path: str) -> str:
        """

        :param absolute_path:
        :return: tuple - (bucket, path)
        """
        return ''

    @abstractmethod
    def add_tags(self, base_path: str, relative_path: str, new_tags: object) -> bool:
        return False

    @abstractmethod
    def get_tags(self, base_path: str, relative_path: str, version_id: str = None) -> dict:
        return {}

    @abstractmethod
    def zipped_upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool,
                      s3_name: Union[str, None], obj_tags: dict, lock: object, overwrite: bool):
        return

    @abstractmethod
    def upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool,
               s3_name: Union[str, None], obj_tags: dict, lock: object, overwrite: bool):
        return

    @abstractmethod
    def bytes_upload(self, base_path: str, relative_parent_path: str, content: bytes):
        return

    @abstractmethod
    def list_recursively(self, base_path: str, relative_parent_path: str, additional_checks: Callable[[str], bool],
                         with_versions: bool):
        return
