# coding: utf-8
import json
import argparse
import logging
import os
import sys

from controller import stats, ServerError

import thriftpy
from thriftpy.rpc import make_server


publication_stats_thrift = thriftpy.load(
    os.path.dirname(__file__)+'/publication_stats.thrift',
    module_name='publication_stats_thrift'
)

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '11600'

def _config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    logging_config = {
        'level': allowed_levels.get(logging_level, 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

    if logging_file:
        logging_config['filename'] = logging_file

    logging.basicConfig(**logging_config)


class Dispatcher(object):

    def __init__(self):

        self._stats = stats()

    def _stats_dispatcher(self, *args, **kwargs):

        try:
            data = self._stats.publication_stats(*args, **kwargs)
        except ValueError as e:
            logging.error(e.message)
            raise publication_stats_thrift.ValueError(message=e.message)
        except ServerError as e:
            raise publication_stats_thrift.ServerError(message=e.message)

        return data

    def query(self, doc_type, body):

        try:
            data = self._stats.publication_search(doc_type, body)
        except ValueError as e:
            logging.error(e.message)
            raise publication_stats_thrift.ValueError(message=e.message)
        except ServerError as e:
            raise publication_stats_thrift.ServerError(message=e.message)

        try:
            data_str = json.dumps(data)
        except ValueError as e:
            logging.error('Invalid JSON data: %s' % data_str)
            raise publication_stats_thrift.ValueError(message=e.message)

        return data_str

    def journal_subject_areas(self, filters=None):

        data = self._stats_dispatcher('journal', 'subject_areas', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_collections(self, filters=None):

        data = self._stats_dispatcher('journal', 'collection', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_statuses(self, filters=None):

        data = self._stats_dispatcher('journal', 'status', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def journal_inclusion_years(self, filters=None):

        data = self._stats_dispatcher('journal', 'included_at_year', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_subject_areas(self, filters=None):

        data = self._stats_dispatcher('article', 'subject_areas', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_collections(self, filters=None):

        data = self._stats_dispatcher('article', 'collection', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_publication_years(self, filters=None):

        data = self._stats_dispatcher('article', 'publication_year', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_languages(self, filters=None):

        data = self._stats_dispatcher('article', 'languages', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_affiliation_countries(self, filters=None):

        data = self._stats_dispatcher('article', 'aff_countries', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]

    def document_types(self, filters=None):

        data = self._stats_dispatcher('article', 'document_type', filters=filters)

        return [publication_stats_thrift.aggs(key=key, count=count) for key, count in data.items()]


def main(host=DEFAULT_HOST, port=DEFAULT_PORT):
    server = make_server(
        publication_stats_thrift.PublicationStats,
        Dispatcher(),
        host,
        port
    )

    logging.info('Starting Server on %s:%s' % (host, port))

    server.serve()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="RPC Server for SciELO Publication Statistics"
    )

    parser.add_argument(
        '--host',
        '-i',
        default=DEFAULT_HOST,
        help='RPC Server host'
    )

    parser.add_argument(
        '--port',
        '-p',
        default=DEFAULT_PORT,
        help='RPC Server port'
    )

    parser.add_argument(
        '--logging_file',
        '-o',
        default='/var/log/rpc_publication_statistics.log',
        help='Full path to the log file'
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logggin level'
    )

    args = parser.parse_args()

    _config_logging(args.logging_level, args.logging_file)

    main(
        host=args.host,
        port=args.port
    )