#!/usr/bin/env bash

# (safely) run a revision command within alembic and optionally reset all the version folder

# check if we have a --reset requested
RESET=0
if [ "$1" = "--reset" ]; then
  RESET=1
  shift
fi

# if reset is requested, then move the backup folder to backup.YYYYMMDDHHMMSS
if [ "$RESET" = "1" ]; then
  # get the current date
  DATE=$(date +%Y%m%d%H%M%S)

  # move the backup folder to backup.YYYYMMDDHHMMSS
  mv ./alembic/versions ./alembic/versions.$DATE
  mkdir ./alembic/versions
fi

# run the revision command
PYTHONPATH=usbills_app alembic revision --autogenerate -m "auto-revision from revision.sh"
