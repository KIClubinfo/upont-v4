#!/usr/bin/env bash

# DB setting
DB_USER=upont
DB_NAME=upont
DB_PASSWORD=upont


# Settings
DATE=$(date +"%Y%m%d%H%M")
CONTAINER_BACKUP_PATH=/backups/database
LOCAL_BACKUP_PATH=$(dirname "$0")/../backups/database

# Create the local backup directory if it doesn't exist
if [ ! -d "$LOCAL_BACKUP_PATH" ]; then
  echo 'Creating the database backup directory'
  mkdir "$LOCAL_BACKUP_PATH"
fi


# Dump the database with django-admin
echo 'Backing up database...'
docker-compose exec back /src/manage.py dumpdata -o "$CONTAINER_BACKUP_PATH/$DATE.json.gz"

# Clean the backup directory, saving only the last 3 backups.
echo 'Cleaning old database backup'
cd "$LOCAL_BACKUP_PATH" || exit; (ls -t|head -n 3;ls)|sort|uniq -u|xargs rm -f
