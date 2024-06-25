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

from ideas_api.lib.utils.factory_abstract import FactoryAbstract


class ESFactory(FactoryAbstract):
    NO_AUTH = 'NO_AUTH'
    AWS = 'AWS'

    def get_instance(self, class_type, **kwargs):
        ct = class_type.upper()
        if ct == self.NO_AUTH:
            from ideas_api.lib.external_io.es_middleware import ESMiddleware
            return ESMiddleware(kwargs['index'], kwargs['base_url'], port=kwargs['port'])
        if ct == self.AWS:
            from ideas_api.lib.external_io.es_middleware_aws import EsMiddlewareAws
            return EsMiddlewareAws(kwargs['index'], kwargs['base_url'], port=kwargs['port'])
        raise ModuleNotFoundError(f'cannot find ES class for {ct}')
