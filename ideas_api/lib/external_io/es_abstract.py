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

DEFAULT_TYPE = '_doc'


class ESAbstract(ABC):
    @abstractmethod
    def create_index(self, index_name, index_body):
        return

    @abstractmethod
    def has_index(self, index_name):
        return

    @abstractmethod
    def create_alias(self, index_name, alias_name):
        return

    @abstractmethod
    def delete_index(self, index_name):
        return

    @abstractmethod
    def index_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        return

    @abstractmethod
    def index_one(self, doc, doc_id, index=None):
        return

    @abstractmethod
    def update_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        return

    @abstractmethod
    def update_one(self, doc, doc_id, index=None):
        return

    @staticmethod
    @abstractmethod
    def get_result_size(result):
        return

    @abstractmethod
    def query_with_scroll(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query_pages(self, dsl, querying_index=None):
        return

    @abstractmethod
    def query_by_id(self, doc_id, querying_index=None):
        return
