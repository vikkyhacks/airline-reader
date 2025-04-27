import logging

import pandas

_LOG = logging.getLogger(__name__)


def read_file(file_path):
    _LOG.info(f"Reading file file_path={file_path}")
    df = pandas.read_excel(file_path)
    return df.to_dict(orient='records')


def write_file(records, file_path):
    _LOG.info(f"Writing file file_path={file_path}; len(records)={len(records)}")
    df = pandas.DataFrame(records)
    df.to_excel(file_path, index=False, engine='openpyxl')
