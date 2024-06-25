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
from io import BytesIO
from typing import Callable, Union

from ideas_api.lib.aws_base.aws_constants import AwsConstants
from ideas_api.lib.aws_base.aws_cred import AwsCred
from ideas_api.lib.external_io.file_stream_abstract import FileStreamAbstract
from ideas_api.lib.utils.fake_lock import FakeLock
from ideas_api.lib.utils.file_utils import FileUtils

LOGGER = logging.getLogger(__name__)


class FileStreamS3(FileStreamAbstract):
    def __init__(self):
        client_params= {
            'service_name': AwsConstants.s3,
        }
        if AwsConstants.s3_endpoint_url in os.environ:
            client_params['endpoint_url'] = os.environ.get(AwsConstants.s3_endpoint_url)
        self.__s3_client = AwsCred().get_client(**client_params)
        self.__up_bucket = None
        self.__up_key = None
        self.__up_parts_dict = {}
        self.__up_part_num = None
        self.__multipart_up = None

    def has_file(self, base_path: str, relative_path: str):
        try:
            response = self.__s3_client.head_object(Bucket=base_path, Key=relative_path)
        except:
            return False
        return True

    def upload_parts_begin(self, base_path: str, relative_path: str, tags: dict = {}):
        self.__up_bucket = base_path
        self.__up_key = relative_path
        self.__up_parts_dict.clear()
        self.__up_part_num = 1
        self.__multipart_up = self.__s3_client.create_multipart_upload(Bucket=base_path,
                                                                       Key=relative_path,
                                                                       ServerSideEncryption='AES256',
                                                                       Tagging=tags)
        self._up_parts_dict = {
            'Parts': []
        }
        return self.__multipart_up['UploadId']

    def upload_part_x(self, body: bytes):
        part1 = self.__s3_client.upload_part(Bucket=self.__up_bucket,
                                             Key=self.__up_key,
                                             PartNumber=self.__up_part_num,
                                             UploadId=self.__multipart_up['UploadId'],
                                             Body=body)
        self._up_parts_dict['Parts'].append({
            'PartNumber': self.__up_part_num,
            'ETag': part1['ETag']
        })
        self.__up_part_num += 1
        return

    def upload_parts_end(self):
        return self.__s3_client.complete_multipart_upload(Bucket=self.__up_bucket,
                                                          Key=self.__up_key,
                                                          UploadId=self.__multipart_up['UploadId'],
                                                          MultipartUpload=self._up_parts_dict)

    def to_url(self, base_path: str, relative_path: str) -> str:
        return f's3://{base_path}/{relative_path}'

    def split_url(self, absolute_path: str) -> tuple:
        if not absolute_path.startswith('s3://'):
            raise ValueError(f'invalid S3 URL. must start with "s3://": {absolute_path}')
        cut_s3_path = absolute_path.replace('s3://', '').replace('file://', '')
        bucket_index = cut_s3_path.find('/')
        return cut_s3_path[0: bucket_index], cut_s3_path[bucket_index + 1:]

    def get_modified_date(self, base_path: str, relative_path: str):
        response = self.__s3_client.head_object(Bucket=base_path, Key=relative_path)
        return response['LastModified'].timestamp()

    def get_size(self, base_path: str, relative_path: str):
        response = self.__s3_client.head_object(Bucket=base_path, Key=relative_path)
        return response['ContentLength']

    def get_all_versions(self, base_path: str, relative_path: str):
        response = self.__s3_client.list_object_versions(
            Bucket=base_path,
            # Delimiter='string',
            # EncodingType='url',
            # KeyMarker='string',
            # MaxKeys=123,
            Prefix=relative_path,
            # VersionIdMarker='string',
            # ExpectedBucketOwner='string'
        )
        if 'Versions' not in response:
            return []
        return response['Versions']

    def get_version(self, base_path: str, relative_path: str):
        response = self.__s3_client.head_object(Bucket=base_path, Key=relative_path)
        if 'VersionId' not in response:
            return None
        return response['VersionId']

    def get_stream(self, base_path, relative_path):
        return self.__s3_client.get_object(Bucket=base_path, Key=relative_path)['Body']

    def delete(self, base_path: str, relative_path: str, version_id: str = None):
        params = {
            'Bucket': base_path,
            'Key': relative_path,
        }
        if version_id is not None:
            params['VersionId'] = version_id
        return self.__s3_client.delete_object(**params)

    def read_text_file(self, base_path: str, relative_path: str):
        """
        convenient method to read small text files stored in S3

        :param base_path: bucket name
        :param relative_path: S3 key
        :return: str - text file contents
        """
        bytestream = BytesIO(self.get_stream(base_path, relative_path).read())  # get the bytes stream of zipped file
        return bytestream.read().decode('UTF-8')

    def download(self, base_path, relative_path, abs_folder_path, local_filename=None):
        try:
            FileUtils.mk_dir_p(abs_folder_path)
            if local_filename is None:
                local_filename = os.path.basename(relative_path)
            local_file_path = os.path.join(abs_folder_path, local_filename)  # create zipped file name
            # download to file. using the builtin method which will work in smaller machines
            self.__s3_client.download_file(base_path, relative_path, local_file_path)
        except Exception as e:
            LOGGER.exception(f'error while downloading `{base_path}:{relative_path} to {abs_folder_path}`. throwing the same exception')
            raise e
        return local_file_path

    def add_tags(self, base_path: str, relative_path: str, new_tags: dict) -> bool:
        """
        retrieve existing tags first and append new tags to them

        :param base_path: string - bucket
        :param relative_path: string - s3 key
        :param new_tags: dict
        :return: bool
        """
        if len(new_tags) == 0:
            return False
        existing_tags = self.get_tags(base_path, relative_path, None)
        if existing_tags is None:
            LOGGER.error(f'error while retrieving existing tags for : {base_path}/{relative_path}')
            return False
        tags = {
            'TagSet': []
        }
        for k, v in existing_tags.items():
            tags['TagSet'].append({
                'Key': k,
                'Value': str(v)
            })
        for key, val in new_tags.items():
            tags['TagSet'].append({
                'Key': key,
                'Value': str(val)
            })
        self.__s3_client.put_object_tagging(Bucket=base_path, Key=relative_path, Tagging=tags)

    def get_tags(self, base_path: str, relative_path: str, version_id: str = None) -> Union[dict, None]:
        """
        returning all the tags in a dictionary form

        :param base_path: bucket
        :param relative_path: s3 key
        :return:
        """
        params = {
            'Bucket': base_path,
            'Key': relative_path,
        }
        if version_id is not None:
            params['VersionId'] = version_id
        response = self.__s3_client.get_object_tagging(**params)
        if 'TagSet' not in response:
            return None
        return {k['Key']: k['Value'] for k in response['TagSet']}

    def __upload_to_s3(self, bucket, prefix, file_path, delete_files=False, add_size=True, other_tags={}, s3_name=None):
        """
        Uploading a file to S3

        :param bucket: string - name of bucket
        :param prefix: string - prefix. don't start and end with `/` to avoid extra unnamed dirs
        :param file_path: string - absolute path of file location
        :param delete_files: boolean - deleting original file. default: False
        :param add_size: boolean - adding the file size as tag. default: True
        :param other_tags: dict - key-value pairs as a dictionary
        :param s3_name: string - name of s3 file if the user wishes to change.
                    using the actual filename if not provided. defaulted to None
        :return: None
        """
        tags = {
            'TagSet': []
        }
        adding_tags = False
        if add_size is True:
            adding_tags = True
            tags['TagSet'].append({
                'Key': 'org_size',
                'Value': str(FileUtils.get_size(file_path))
            })
        for key, val in other_tags.items():
            tags['TagSet'].append({
                'Key': key,
                'Value': str(val)
            })
        if s3_name is None:
            s3_name = os.path.basename(file_path)
        s3_key = '{}/{}'.format(prefix, s3_name)
        self.__s3_client.upload_file(file_path, bucket, s3_key, ExtraArgs={'ServerSideEncryption': 'AES256'})
        if delete_files is True:  # deleting local files
            FileUtils.remove_if_exists(file_path)
        if adding_tags is True:
            try:
                self.__s3_client.put_object_tagging(Bucket=bucket, Key=s3_key, Tagging=tags)
            except Exception as e:
                LOGGER.exception(f'error while adding tags: {tags} to {bucket}/{s3_key}')
                raise e
        return

    def zipped_upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool = False, s3_name: str = None,
                      obj_tags: dict = {}, lock: object = FakeLock(), overwrite: bool = False):
        """
        Zipping a file and uploading to s3

        zipping in gzip form with compression level 9

        :param file_path: string - absolute path of the file on disk
        :param base_path: string - s3 bucket
        :param relative_parent_path: string - prefix of s3 (must not start and end with `/`)
        :param delete_files: boolean - if file on disk is deleted. defaulted to False
        :param s3_name: string - name of s3 file if the user wishes to change.
                    using the actual filename if not provided. defaulted to None
        :param obj_tags: dict - dictionary of tags to be attached to the object
        :param lock: obj - a lock object for parallel processing. defaulted to an empty lock if absent
        :param overwrite: bool - not in used at this moment
        :return: None
        """
        LOGGER.info(f'base_path: {base_path} -- relative_parent_path: {relative_parent_path}')
        tags = deepcopy(obj_tags)
        tags['unzipped_size'] = FileUtils.get_size(file_path)
        zipped_file_path = '{}.gz'.format(file_path)
        FileUtils.gzip_file_unix_os(file_path, zipped_file_path, True)
        with lock:
            self.__upload_to_s3(base_path, relative_parent_path, zipped_file_path, delete_files, True, tags, s3_name)
        if delete_files is True:  # deleting local files
            FileUtils.remove_if_exists(file_path)

    def __get_all_s3_files_under(self, bucket, prefix, with_versions=False):
        list_method_name = 'list_object_versions' if with_versions is True else 'list_objects_v2'
        page_key = 'Versions' if with_versions is True else 'Contents'
        paginator = self.__s3_client.get_paginator(list_method_name)
        operation_parameters = {
            'Bucket': bucket,
            'Prefix': prefix
        }
        page_iterator = paginator.paginate(**operation_parameters)
        for eachPage in page_iterator:
            if page_key not in eachPage:
                continue
            for fileObj in eachPage[page_key]:
                yield fileObj
        return

    def list_recursively(self, base_path: str, relative_parent_path: str,
                         additional_checks: Callable[[str], bool] = lambda x: True,
                         with_versions: bool = False):
        for fileObj in self.__get_all_s3_files_under(base_path, relative_parent_path, with_versions=with_versions):
            if additional_checks(fileObj):
                yield fileObj['Key'], fileObj['Size']
        return

    def upload(self, file_path: str, base_path: str, relative_parent_path: str, delete_files: bool,
               s3_name: Union[str, None] = None, obj_tags: dict = {}, lock: object = FakeLock(), overwrite: bool = False):
        with lock:
            self.__upload_to_s3(base_path, relative_parent_path, file_path, delete_files, True, obj_tags, s3_name)
        if delete_files is True:  # deleting local files
            FileUtils.remove_if_exists(file_path)
        return

    def bytes_upload(self, base_path: str, relative_parent_path: str, content: bytes):
        try:
            self.__s3_client.put_object(Bucket=base_path,
                                        Key=relative_parent_path,
                                        ContentType='binary/octet-stream',
                                        Body=content,
                                        ServerSideEncryption='AES256')
        except BaseException:
            LOGGER.exception(f'failed to upload stream to {base_path}:{relative_parent_path}')
        return True
