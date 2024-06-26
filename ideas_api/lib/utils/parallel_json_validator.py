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
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fastjsonschema
import logging
from datetime import datetime
from multiprocessing import Pool
from ideas_api.lib.utils.singleton_base import Singleton

LOGGER = logging.getLogger(__name__)


def __validate_small_data(small_data):
    validator = ParallelJsonValidator()
    try:
        validator.schema(small_data)
        return None
    except Exception as e:
        return str(e)


def parallel_validate(chunked_data):
    a = datetime.now()
    with Pool(16) as p:
        all_result = p.map(__validate_small_data, chunked_data)
    all_result = [k for k in all_result if k is not None]
    b = datetime.now()
    LOGGER.debug(f'validation took: {b - a}')
    return len(all_result) < 1, all_result


class ParallelJsonValidator(metaclass=Singleton):
    def __init__(self):
        self.__schema = None

    @property
    def schema(self):
        return self.__schema

    @schema.setter
    def schema(self, val):
        """
        :param val:
        :return: None
        """
        self.__schema = fastjsonschema.compile(val)
        return

    def load_schema(self, input_schema):
        self.schema = input_schema
        return self

    def is_schema_loaded(self):
        return self.__schema is not None

    def __validate_this(self, small_data):
        try:
            self.__schema(small_data)
            return None
        except Exception as e:
            return str(e)

    def validate_json(self, chunked_data: list):
        if self.is_schema_loaded() is False:
            raise ValueError(f'schema is not loaded. cannot validate')
        if len(chunked_data) < 1:
            LOGGER.debug(f'no need to validate empty json')
            return True
        LOGGER.debug(f'chunked_data size: {len(chunked_data)}')
        return parallel_validate(chunked_data)


class SingleJsonValidator(object):
    def __init__(self):
        self.__schema = None

    @property
    def schema(self):
        return self.__schema

    @schema.setter
    def schema(self, val):
        """
        :param val:
        :return: None
        """
        self.__schema = fastjsonschema.compile(val)
        return

    def load_schema(self, input_schema):
        self.schema = input_schema
        return self

    def validate(self, input_data):
        try:
            self.schema(input_data)
        except Exception as e:
            return False, str(e)
        return True, None
