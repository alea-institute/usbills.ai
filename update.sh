#!/usr/bin/env bash

# export GOVINFO_API_KEY=
PYTHONPATH=. poetry run python3 usbills_app/cli/update_bills.py
PYTHONPATH=. poetry run python3 usbills_app/cli/load_bill_json.py ~/.cache/fbs/bills/
PYTHONPATH=. poetry run python3 usbills_app/cli/update_bill_percentiles.py
PYTHONPATH=. poetry run python3 usbills_app/cli/load_solr.py
PYTHONPATH=. poetry run python3 usbills_app/cli/clear_cache.py
PYTHONPATH=. poetry run python3 usbills_app/cli/generate_sitemap.py
