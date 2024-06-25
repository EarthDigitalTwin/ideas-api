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

from ideas_api.lib.external_io.file_stream_local import FileStreamLocal
from ideas_api.lib.external_io.file_stream_s3 import FileStreamS3
from ideas_api.lib.utils.factory_abstract import FactoryAbstract

LOGGER = logging.getLogger(__name__)


class FileStreamFactory(FactoryAbstract):
    def get_instance(self, file_repo, **kwargs):
        fr = file_repo.upper()
        if fr == 'LOCAL':
            return FileStreamLocal()
        if fr == 'S3':
            return FileStreamS3()
        raise ModuleNotFoundError(f'cannot find FileStream class for {fr}')
