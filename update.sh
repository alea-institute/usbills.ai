#!/usr/bin/env bash

echo "Starting update script..."


pipx ensurepath
echo "Set pipx path"
export PATH="$PATH:/home/ubuntu/.local/bin/"

pushd /home/ubuntu/usbills.ai
echo "Set working dir"

export GOVINFO_API_KEY=
export PYTHONPATH=.
echo "Set path"

poetry run python3 usbills_app/cli/update_bills.py
poetry run python3 usbills_app/cli/load_bill_json.py ~/.cache/fbs/bills/
poetry run python3 usbills_app/cli/update_bill_percentiles.py
poetry run python3 usbills_app/cli/load_solr.py
poetry run python3 usbills_app/cli/clear_cache.py
poetry run python3 usbills_app/cli/generate_sitemap.py

popd
echo "Returned working dir"
