import logging

from requests import HTTPError

from airlines_reader.airlines import booking_details, AirlineModelBuilder
from airlines_reader.file_handler import read_file
from airlines_reader.file_handler.file_handler import write_file
from airlines_reader.utils import setup_logging

setup_logging()

_LOG = logging.getLogger(__name__)


def _enrich_record(record):
    pnr = record["PNR"]
    name = record['NAME']
    _LOG.info(f"Enriching record pnr={pnr} name={name}")
    try:
        raw_booking_dump = booking_details(pnr, name)
        parsed_booking_info = AirlineModelBuilder(raw_booking_dump).build().to_dict()
        new_dict = dict(record)
        new_dict.update(parsed_booking_info)
        return new_dict
    except HTTPError:
        _LOG.error(f"Received HTTPError; skipping record pnr={pnr} name={name}")
        return record
    except Exception:
        _LOG.exception(f"Unknown error; skipping record pnr={pnr} name={name}")
        return record


def main(input_fp, output_fp):
    records = read_file(input_fp)
    enriched_records = [
        _enrich_record(record)
        for record in records
    ]
    write_file(enriched_records, output_fp)


if __name__ == "__main__":
    main("/Users/vigneshkp/Downloads/ADD TO BOM 610 & 640.xlsx", "/Users/vigneshkp/Downloads/out.xlsx")
