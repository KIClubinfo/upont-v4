#!/usr/bin/env bash

# Stop the script if an error occurs
set -e

# DB setting
DB_USER=upont
DB_NAME=upont

# Settings
DATE=$(date +"%Y%m%d%H%M")
CONTAINER_BACKUP_PATH=/backups/database
LOCAL_BACKUP_PATH=$(dirname "$0")/../backups/database

# Create the local backup directory if it doesn't exist
if [ ! -d "$LOCAL_BACKUP_PATH" ]; then
  echo 'Creating the database backup directory'
  mkdir "$LOCAL_BACKUP_PATH"
fi

if [ -d "$LOCAL_BACKUP_PATH" ]; then
  # Dump the database with django-admin
  echo 'Backing up database...'
  docker-compose exec db /bin/bash -c "pg_dump -U \"$DB_USER\" -Fc \"$DB_NAME\" --exclude-table=django_migrations > \"$CONTAINER_BACKUP_PATH/$DATE.dump\""

  # Clean the backup directory, saving only the last 3 backups.
  echo 'Cleaning old database backup'
  cd "$LOCAL_BACKUP_PATH" || exit; (ls -t|head -n 3;ls)|sort|uniq -u|xargs rm -f
else
  echo "Database save path doesn't exit"
  echo 'The database has not been saved'
  exit 1
fi