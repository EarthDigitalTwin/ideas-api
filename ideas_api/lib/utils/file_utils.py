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

import gzip
import json
import logging
import os
import shutil
import tarfile
import zipfile
from pathlib import Path
from subprocess import Popen, PIPE

module_log = logging.getLogger(__name__)


class FileUtils:
    @staticmethod
    def copy_file(abs_src_file_path, abs_dest_dir_path, new_file_name=None, overwrite=False):
        """
        copy file in local disk
        :param abs_src_file_path: absolute source file path. error will be thrown if missing
        :param abs_dest_dir_path: str - absolute destination directory path. It will be created if missing
        :param new_file_name: str - destination filename if wants to be renamed. defaulted to None
        :param overwrite: bool - if it will copy if destination file exist. error will be thrown if necessary
        :return: str - absolute destination file path
        """
        error_list = []
        if not FileUtils.file_exist(abs_src_file_path):
            error_list.append('missing source file: {}'.format(abs_src_file_path))
        FileUtils.mk_dir_p(abs_dest_dir_path)
        abs_dest_file_path = os.path.join(abs_dest_dir_path, os.path.basename(abs_src_file_path) if new_file_name is None else new_file_name)
        if overwrite is False and FileUtils.file_exist(abs_dest_file_path):
            error_list.append('destination file exists, and not overwriting: {}'.format(abs_dest_file_path))
        if len(error_list) > 0:
            raise ValueError('errors while attempting to copy file: {}'.format(error_list))
        if abs_src_file_path == abs_dest_file_path:  # no need to copy
            return abs_dest_file_path
        shutil.copyfile(abs_src_file_path, abs_dest_file_path)
        return abs_dest_file_path

    @staticmethod
    def get_size(abs_file_path):
        if not FileUtils.file_exist(abs_file_path):
            raise ValueError(f'missing file: {abs_file_path}')
        return os.stat(abs_file_path).st_size

    @staticmethod
    def get_modified_time(abs_file_path):
        if not FileUtils.file_exist(abs_file_path):
            raise ValueError(f'missing file: {abs_file_path}')
        return os.stat(abs_file_path).st_mtime

    @staticmethod
    def is_0_byte_file(abs_file_path):
        return FileUtils.get_size(abs_file_path) < 1

    @staticmethod
    def file_exist(abs_file_path):
        """
        helper file

        :param abs_file_path: string - absolute file path to the file
        :return: bool
        """
        return os.path.exists(abs_file_path) and os.path.isfile(abs_file_path)

    @staticmethod
    def dir_exist(abs_dir_path):
        """
        helper file

        :param abs_dir_path: string - absolute path to the directory
        :return: bool
        """
        return os.path.exists(abs_dir_path) and os.path.isdir(abs_dir_path)

    @staticmethod
    def mk_dir_p(dir_path):
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return

    @staticmethod
    def remove_if_exists(file_path):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
        return

    @staticmethod
    def read_small_text_file(file_path):
        if not FileUtils.file_exist(file_path):
            raise IOError('{} does not exist'.format(file_path))
        with open(file_path, 'r') as ff:
            return ff.read()

    @staticmethod
    def read_json_file(file_path):
        if not os.path.exists(file_path):
            raise IOError('{} does not exist'.format(file_path))
        try:
            with open(file_path, 'r') as ff:
                return json.loads(ff.read())
            pass
        except:
            module_log.exception('error converting to json for {}'.format(file_path))
        return {}

    @staticmethod
    def read_json_nl_file(file_path):
        """
        Helper function where it reads each line of a given file which is a json document.
        It parses each line into a json doc and returns it.

        For those invalid lines, it is currently ignored and thrown into log. It might need to be updated in next iteration.

        :param file_path: absolute / relative file path
        :return: yielding each json document
        """
        if not os.path.exists(file_path):
            raise IOError('{} does not exist'.format(file_path))
        try:
            with open(file_path, 'r') as ff:
                return [json.loads(k) for k in ff.readlines()]
            pass
        except:
            module_log.exception('error converting to json for {}'.format(file_path))
        return []

    @staticmethod
    def write_json_file(file_path, json_obj, overwrite=False, append=False, prettify=False):
        if os.path.exists(file_path) and not overwrite:
            raise ValueError('{} already exists, and not overwriting'.format(file_path))
        with open(file_path, 'a' if append else 'w') as ff:
            json_str = json.dumps(json_obj, indent=4) if prettify else json.dumps(json_obj)
            ff.write(json_str)
            pass
        return

    @staticmethod
    def write_json_nl_file(file_path, json_nl, overwrite=False, append=False):
        if os.path.exists(file_path) and not overwrite:
            raise ValueError('{} already exists, and not overwriting'.format(file_path))
        with open(file_path, 'a' if append else 'w') as ff:
            ff.write('\n'.join(json.dumps(k) for k in json_nl))
            pass
        return

    @staticmethod
    def tar_immediate_dir_unix(dir_path, tar_file_path, delete_files=False):
        if not FileUtils.dir_exist(dir_path):
            raise ValueError('missing dir: {}'.format(dir_path))
        session = Popen(['tar', '-cvf', tar_file_path, dir_path], stdout=PIPE, stderr=PIPE)
        stdout, stderr = session.communicate()
        if stderr:
            raise RuntimeError(f'error while tarring the file with Popen. filename: {tar_file_path}. error: {stderr}')
        if delete_files:
            for eachFile in os.listdir(dir_path):  # tar is done. delete all files inside the dir
                FileUtils.remove_if_exists(os.path.join(dir_path, eachFile))
        if not FileUtils.file_exist(tar_file_path):
            raise ValueError(f'missing tar_file_path: {tar_file_path}')
        return

    @staticmethod
    def tar_immediate_dir(dir_path, tar_file_path, delete_files=False):
        dir_files = os.listdir(dir_path)  # all files in the dir. need to save this so that the tar is not deleted.
        with tarfile.open(tar_file_path, "w:gz") as tar:  # tarring the directory
            tar.add(dir_path, arcname=os.path.basename(tar_file_path).replace('.tar', ''))
            pass
        if not delete_files:
            return
        for eachFile in dir_files:  # tar is done. delete all files inside the dir
            FileUtils.remove_if_exists(os.path.join(dir_path, eachFile))
            pass
        if len(os.listdir(dir_path)) < 1:
            os.rmdir(dir_path)
        return

    @staticmethod
    def zip_immediate_dir_unix(dir_path, zip_file_name, delete_files=False):
        if not FileUtils.dir_exist(dir_path):
            raise ValueError('missing dir: {}'.format(dir_path))
        session = Popen(['zip', '-r', zip_file_name, dir_path], stdout=PIPE, stderr=PIPE)
        stdout, stderr = session.communicate()
        if stderr:
            raise RuntimeError(f'error while zipping the file with Popen. filename: {zip_file_name}. error: {stderr}')
        if delete_files:
            for eachFile in os.listdir(dir_path):  # tar is done. delete all files inside the dir
                FileUtils.remove_if_exists(os.path.join(dir_path, eachFile))
        if not FileUtils.file_exist(zip_file_name):
            raise ValueError(f'missing zip_file_name: {zip_file_name}')
        return

    @staticmethod
    def zip_immediate_dir(dir_path, zip_file_name, delete_files=False):
        dir_files = os.listdir(dir_path)  # all files in the dir. need to save this so that the tar is not deleted.
        arc_base_name = os.path.basename(zip_file_name).replace('.zip', '')
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for eachFile in dir_files:
                zipf.write(os.path.join(dir_path, eachFile), arcname=os.path.join(arc_base_name, eachFile))
                pass
            pass
        if not delete_files:
            return
        for eachFile in dir_files:  # tar is done. delete all files inside the dir
            FileUtils.remove_if_exists(os.path.join(dir_path, eachFile))
            pass
        if len(os.listdir(dir_path)) < 1:
            os.rmdir(dir_path)
        return

    @staticmethod
    def gunzip_file_lib(zipped_file_path, output_file_path=None, buffer_size=50 * 2 ** 20):
        empty_byte = ''.encode()
        if output_file_path is None:
            output_file_path = os.path.join(os.path.dirname(zipped_file_path),
                                            os.path.basename(zipped_file_path)[:-3])  # create unzipped file name
        with gzip.GzipFile(zipped_file_path, 'rb') as in_f:  # unzipping the file using gzip
            with open(output_file_path, 'wb') as outF:
                while True:
                    data = in_f.read(buffer_size)
                    if data == empty_byte:
                        break
                    outF.write(data)
        return output_file_path

    @staticmethod
    def gzip_file_unix_os(file_path, output_file_path=None, overwrite=False):
        if not FileUtils.file_exist(file_path):
            raise ValueError(f'missing file: {file_path}')
        default_output_path = f'{file_path}.gz'
        if output_file_path is None:
            output_file_path = default_output_path
        if FileUtils.file_exist(output_file_path) and overwrite is False:
            raise ValueError(f'zipped file already exists: {output_file_path} and overwrite is set to False')
        session = Popen(['gzip', '-9', file_path], stdout=PIPE, stderr=PIPE)
        stdout, stderr = session.communicate()
        if stderr:
            raise RuntimeError(
                'error while gunzipping the file with Popen. filename: {}. error: {}'.format(file_path, stderr))
        if not FileUtils.file_exist(default_output_path):
            raise ValueError('missing gzipped file: {}'.format(default_output_path))
        if default_output_path != output_file_path:
            os.renames(default_output_path, output_file_path)
        return output_file_path

    @staticmethod
    def gunzip_file_os(zipped_file_path, output_file_path=None):
        if not FileUtils.file_exist(zipped_file_path):
            raise ValueError('missing file: {}'.format(zipped_file_path))
        session = Popen(['gunzip', zipped_file_path], stdout=PIPE, stderr=PIPE)
        stdout, stderr = session.communicate()
        if stderr:
            raise RuntimeError('error while gunzipping the file with Popen. filename: {}. error: {}'.format(zipped_file_path, stderr))
        default_output_path = zipped_file_path[:-3]
        if not FileUtils.file_exist(default_output_path):
            raise ValueError('missing gunzipped file: {}'.format(default_output_path))
        if output_file_path is None:
            output_file_path = default_output_path
        if FileUtils.file_exist(output_file_path) and default_output_path != output_file_path:
            os.renames(default_output_path, output_file_path)
        return output_file_path

    @staticmethod
    def delete_directory_force(dir_path):
        shutil.rmtree(dir_path, True)
        return
    pass
