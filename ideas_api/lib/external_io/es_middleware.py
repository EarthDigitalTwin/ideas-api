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

import json
import logging

from elasticsearch import Elasticsearch

from ideas_api.lib.external_io.es_abstract import ESAbstract, DEFAULT_TYPE

LOGGER = logging.getLogger(__name__)


class ESMiddleware(ESAbstract):

    def __init__(self, index, base_url, port=443) -> None:
        if any([k is None for k in [index, base_url]]):
            raise ValueError(f'index or base_url is None')
        self.__index = index
        base_url = base_url.replace('https://', '')  # hide https
        self._engine = Elasticsearch(hosts=[{'host': base_url, 'port': port}])

    def __validate_index(self, index):
        if index is not None:
            return index
        if self.__index is not None:
            return self.__index
        raise ValueError('index value is NULL')

    def __get_doc_dict(self, docs=None, doc_ids=None, doc_dict=None):
        if doc_dict is None and (docs is None and doc_ids is None):
            raise ValueError('must provide either doc dictionary or doc list & id list')
        if doc_dict is None:  # it comes as a list
            if len(docs) != len(doc_ids):
                raise ValueError('length of doc and id is different')
            doc_dict = {k: v for k, v in zip(doc_ids, docs)}
            pass
        return doc_dict

    def __check_errors_for_bulk(self, index_result):
        if 'errors' not in index_result or index_result['errors'] is False:
            return
        err_list = [[{'id': v['_id'], 'error': v['error']} for _, v in each.items() if 'error' in v] for each in
                    index_result['items']]
        if len(err_list) < 1:
            return
        LOGGER.exception('failed to add some items. details: {}'.format(err_list))
        return err_list

    def create_index(self, index_name, index_body):
        result = self._engine.indices.create(index=index_name, body=index_body, include_type_name=False)
        if 'acknowledged' not in result:
            return result
        return result['acknowledged']

    def has_index(self, index_name):
        result = self._engine.indices.exists(index=index_name)
        return result

    def create_alias(self, index_name, alias_name):
        result = self._engine.indices.put_alias(index_name, alias_name)
        if 'acknowledged' not in result:
            return result
        return result['acknowledged']

    def delete_index(self, index_name):
        result = self._engine.indices.delete(index_name)
        if 'acknowledged' not in result:
            return result
        return result['acknowledged']

    def index_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        doc_dict = self.__get_doc_dict(docs, doc_ids, doc_dict)
        body = []
        for k, v in doc_dict.items():
            body.append({'index': {'_index': index, '_id': k, 'retry_on_conflict': 3}})
            body.append(v)
            pass
        index = self.__validate_index(index)
        try:
            index_result = self._engine.bulk(index=index,
                                              body=body, doc_type=DEFAULT_TYPE)
            LOGGER.info('indexed. result: {}'.format(index_result))
            return self.__check_errors_for_bulk(index_result)
        except:
            LOGGER.exception('cannot add indices with ids: {} for index: {}'.format(list(doc_dict.keys()), index))
            return doc_dict
        return

    def index_one(self, doc, doc_id, index=None):
        index = self.__validate_index(index)
        try:
            index_result = self._engine.index(index=index,
                                              body=doc, doc_type=DEFAULT_TYPE, id=doc_id)
            LOGGER.info('indexed. result: {}'.format(index_result))
        except Exception as e:
            LOGGER.exception('cannot add a new index with id: {} for index: {}'.format(doc_id, index))
            raise e
        return self

    def update_many(self, docs=None, doc_ids=None, doc_dict=None, index=None):
        doc_dict = self.__get_doc_dict(docs, doc_ids, doc_dict)
        body = []
        for k, v in doc_dict.items():
            body.append({'update': {'_index': index, '_id': k, 'retry_on_conflict': 3}})
            body.append({'doc': v, 'doc_as_upsert': True})
            pass
        index = self.__validate_index(index)
        try:
            index_result = self._engine.bulk(index=index,
                                             body=body, doc_type=DEFAULT_TYPE)
            LOGGER.info('indexed. result: {}'.format(index_result))
            return self.__check_errors_for_bulk(index_result)
        except:
            LOGGER.exception('cannot update indices with ids: {} for index: {}'.format(list(doc_dict.keys()),
                                                                                             index))
            return doc_dict
        return

    def update_one(self, doc, doc_id, index=None):
        update_body = {
            'doc': doc,
            'doc_as_upsert': True
        }
        index = self.__validate_index(index)
        try:
            update_result = self._engine.update(index=index,
                                                id=doc_id, body=update_body, doc_type=DEFAULT_TYPE)
            LOGGER.info('updated. result: {}'.format(update_result))
        except:
            LOGGER.exception('cannot update id: {} for index: {}'.format(doc_id, index))
            return None
        return self

    @staticmethod
    def get_result_size(result):
        if isinstance(result['hits']['total'], dict):  # fix for different datatype in elastic-search result
            return result['hits']['total']['value']
        else:
            return result['hits']['total']

    def query_with_scroll(self, dsl, querying_index=None):
        scroll_timeout = '30s'
        index = self.__validate_index(querying_index)
        dsl['size'] = 10000  # replacing with the maximum size to minimize number of scrolls
        params = {
            'index': index,
            'size': 10000,
            'scroll': scroll_timeout,
            'body': dsl,
        }
        first_batch = self._engine.search(**params)
        total_size = self.get_result_size(first_batch)
        current_size = len(first_batch['hits']['hits'])
        scroll_id = first_batch['_scroll_id']
        while current_size < total_size:  # need to scroll
            scrolled_result = self._engine.scroll(scroll_id=scroll_id, scroll=scroll_timeout)
            scroll_id = scrolled_result['_scroll_id']
            scrolled_result_size = len(scrolled_result['hits']['hits'])
            if scrolled_result_size == 0:
                break
            else:
                current_size += scrolled_result_size
                first_batch['hits']['hits'].extend(scrolled_result['hits']['hits'])
        return first_batch

    def query(self, dsl, querying_index=None):
        index = self.__validate_index(querying_index)
        return self._engine.search(body=dsl, index=index)

    def __is_querying_next_page(self, targeted_size: int, current_size: int, total_size: int):
        if targeted_size < 0:
            return current_size > 0
        return current_size > 0 and total_size < targeted_size

    def query_pages(self, dsl, querying_index=None):
        if 'sort' not in dsl:
            raise ValueError('missing `sort` in DSL. Make sure sorting is unique')
        index = self.__validate_index(querying_index)
        targeted_size = dsl['size'] if 'size' in dsl else -1
        dsl['size'] = 10000  # replacing with the maximum size to minimize number of scrolls
        params = {
            'index': index,
            'size': 10000,
            'body': dsl,
        }
        LOGGER.debug(f'dsl: {dsl}')
        result_list = []
        total_size = 0
        result_batch = self._engine.search(**params)
        result_list.extend(result_batch['hits']['hits'])
        current_size = len(result_batch['hits']['hits'])
        total_size += current_size
        while self.__is_querying_next_page(targeted_size, current_size, total_size):
            params['body']['search_after'] = result_batch['hits']['hits'][-1]['sort']
            result_batch = self._engine.search(**params)
            result_list.extend(result_batch['hits']['hits'])
            current_size = len(result_batch['hits']['hits'])
            total_size += current_size
        return {
            'hits':  {
                'hits': result_list,
                'total': total_size,
            }
        }

    def query_by_id(self, doc_id, querying_index=None):
        index = self.__validate_index(querying_index)
        dsl = {
            'query': {
                'term': {'_id': doc_id}
            }
        }
        result = self._engine.search(index=index, body=dsl)
        if self.get_result_size(result) < 1:
            return None
        return result['hits']['hits'][0]
