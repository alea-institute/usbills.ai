#!/usr/bin/env bash

# (safely) run a revision command within alembic and optionally reset all the version folder

# run the revision command
PYTHONPATH=usbills_app alembic upgrade head
