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

import logging
import os
from copy import deepcopy
from glob import glob
from typing import Union

from ideas_api.lib.external_io.file_stream_abstract import FileStreamAbstract
from ideas_api.lib.utils.fake_lock import FakeLock
from ideas_api.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class FileStreamLocal(FileStreamAbstract):

    def __init__(self) -> None:
        super().__init__()
        self.__tags_file_postfix = '__tags.json'
        self.__uploading_parts_file_obj = None
        self.__uploading_parts_file_path = None
        self.__uploading_parts_file_tags = None

    def has_file(self, base_path: str, relative_path: str):
        return FileUtils.file_exist(os.path.join(base_path, relative_path))

    def upload_parts_begin(self, base_path: str, relative_path: str, obj_tags: dict = {}):
        self.__uploading_parts_file_path = os.path.join(base_path, relative_path)
        self.__uploading_parts_file_tags = deepcopy(obj_tags)
        FileUtils.mk_dir_p(os.path.dirname(self.__uploading_parts_file_path))
        self.__uploading_parts_file_obj = open(self.__uploading_parts_file_path, 'wb')
        return

    def upload_part_x(self, content: bytes):
        if self.__uploading_parts_file_obj is None:
            return
        self.__uploading_parts_file_obj.write(content)
        return

    def upload_parts_end(self):
        if self.__uploading_parts_file_obj is None:
            return
        self.__uploading_parts_file_obj.close()
        self.__uploading_parts_file_tags['org_size'] = FileUtils.get_size(self.__uploading_parts_file_path)
        if self.__uploading_parts_file_tags:
            FileUtils.write_json_file(f'{self.__uploading_parts_file_path}{self.__tags_file_postfix}', self.__uploading_parts_file_tags, overwrite=True)
        return

    def to_url(self, base_path: str, relative_path: str) -> str:
        return f'file://{os.path.join(base_path, relative_path)}'

    def split_url(self, absolute_path: str) -> tuple:
        """
        for local file system, there is no way to differentiate the bucket and relative path.
        But it will work either way since it's local file system.
        :param absolute_path:
        :return:
        """
        if not absolute_path.startswith('file://') and not absolute_path.startswith('/'):
            raise ValueError(f'invalid S3 URL. must start with "file://" or "/": {absolute_path}')
        return '', absolute_path.replace('file://', '')

    def get_modified_date(self, base_path: str, relative_path: str):
        abs_path = os.path.join(base_path, relative_path)
        if not FileUtils.file_exist(abs_path):
            raise ValueError(f'missing file to get_size: {abs_path}')
        return FileUtils.get_modified_time(abs_path)

    def get_size(self, base_path: str, relative_path: str):
        abs_path = os.path.join(base_path, relative_path)
        if not FileUtils.file_exist(abs_path):
            raise ValueError(f'missing file to get_size: {abs_path}')
        return FileUtils.get_size(abs_path)

    def get_all_versions(self, base_path: str, relative_path: str):
        raise NotImplementedError(f'get_all_versions is not supported for FileStreamLocal at this moment. Pls implement it if needed and applicable')

    def get_version(self, base_path: str, relative_path: str):
        raise NotImplementedError(f'get_version is not supported for FileStreamLocal at this moment. Pls implement it if needed and applicable')

    def delete(self, base_path: str, relative_path: str, version_id: str = None):
        FileUtils.remove_if_exists(os.path.join(base_path, relative_path))
        return

    def read_text_file(self, base_path: str, relative_path: str):
        abs_path = os.path.join(base_path, relative_path)
        if not FileUtils.file_exist(abs_path):
            LOGGER.error(f'attempting to read small file which does not exist: {abs_path}')
            return ''
        return FileUtils.read_small_text_file(abs_path)

    def get_stream(self, base_path, relative_path):
        abs_file_path = os.path.join(base_path, relative_path)
        LOGGER.debug(f'creating a stream for file: {abs_file_path}')
        if not FileUtils.file_exist(abs_file_path):
            raise IOError(f'missing file: {abs_file_path}')
        return open(abs_file_path, 'rb')

    def download(self, base_path, relative_path, abs_folder_path, local_filename=None) -> str:
        """
        For local file storage: it's just a copy function
        :param base_path:
        :param relative_path:
        :param abs_folder_path:
        :param local_filename:
        :return:
        """
        return FileUtils.copy_file(os.path.join(base_path, relative_path), abs_folder_path, local_filename)

    def add_tags(self, base_path: str, relative_path: str, new_tags: object) -> bool:
        if not new_tags:
            LOGGER.debug(f'empty tags. not updating')
            return False
        existing_tags = self.get_tags(base_path, relative_path)
        updated_tags = {**existing_tags, **new_tags}
        FileUtils.write_json_file(os.path.join(base_path, f'{relative_path}{self.__tags_file_postfix}'), updated_tags, overwrite=True)
        return True

    def get_tags(self, base_path: str, relative_path: str, version_id: str = None) -> dict:
        # TODO version_id is not applicable for local system at this moment.
        tags_filepath = os.path.join(base_path, f'{relative_path}{self.__tags_file_postfix}')
        if not FileUtils.file_exist(tags_filepath):
            LOGGER.debug(f'missing tags file: {tags_filepath}. return empty dict')
            return {}
        return FileUtils.read_json_file(tags_filepath)

    def bytes_upload(self, base_path: str, relative_parent_path: str, content: bytes):
        abs_filepath = os.path.join(base_path, relative_parent_path)
        FileUtils.mk_dir_p(os.path.dirname(abs_filepath))
        with open(abs_filepath, 'w') as ff:
            ff.write(content.decode())
        return abs_filepath

    def list_recursively(self, base_path: str, relative_parent_path: str, additional_checks=lambda x: True, with_versions: bool=False):
        for each in glob(os.path.join(base_path, relative_parent_path, '*')):
            if not each.endswith(self.__tags_file_postfix) and additional_checks(each):
                yield each.replace(base_path, '')[1:], FileUtils.get_size(each)
        for each in glob(os.path.join(base_path, relative_parent_path, '**', '*')):
            if not each.endswith(self.__tags_file_postfix) and additional_checks(each):
                yield each.replace(base_path, '')[1:], FileUtils.get_size(each)
        return

    def upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool,
               s3_name: Union[str, None] = None, obj_tags: dict = {}, lock: object = FakeLock(),
               overwrite: bool = False):
        if not FileUtils.file_exist(file_path):
            raise IOError(f'missing file: {file_path}')
        dest_dir = os.path.join(base_path, relative_parent_path)
        FileUtils.mk_dir_p(dest_dir)
        FileUtils.copy_file(file_path, dest_dir, s3_name, overwrite)
        dest_filepath = os.path.join(dest_dir, os.path.basename(file_path) if s3_name is None else s3_name)
        if not FileUtils.file_exist(dest_filepath):
            raise IOError(f'missing copied/uploaded file: {dest_filepath}')
        obj_tags['unzipped_size'] = FileUtils.get_size(file_path)
        obj_tags['org_size'] = FileUtils.get_size(dest_filepath)
        if obj_tags:
            FileUtils.write_json_file(f'{dest_filepath}{self.__tags_file_postfix}', obj_tags, overwrite=True)
        if delete_files is True:
            FileUtils.remove_if_exists(file_path)

    def zipped_upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool = False,
                      s3_name: str = None, obj_tags: dict = {}, lock: object = FakeLock(), overwrite=False):
        if not FileUtils.file_exist(file_path):
            raise IOError(f'missing file: {file_path}')
        dest_dir = os.path.join(base_path, relative_parent_path)
        FileUtils.mk_dir_p(dest_dir)
        dest_filepath = os.path.join(dest_dir, f'{os.path.basename(file_path)}.gz' if s3_name is None else s3_name)
        LOGGER.debug(f'zipping file from {file_path} to {dest_filepath}')
        obj_tags['unzipped_size'] = FileUtils.get_size(file_path)
        FileUtils.gzip_file_unix_os(file_path, dest_filepath, overwrite)
        obj_tags['org_size'] = FileUtils.get_size(dest_filepath)
        if obj_tags:
            FileUtils.write_json_file(f'{dest_filepath}{self.__tags_file_postfix}', obj_tags, overwrite=True)
        if delete_files is True:
            FileUtils.remove_if_exists(file_path)
        return
