#!/bin/bash

# Stop the script if an error occurs
set -e

# Settings
DATE=$(date +"%Y%m%d%H%M")
APPLICATION_PATH=/src/media
CONTAINER_BACKUP_PATH=/backups/media
LOCAL_BACKUP_PATH=$(dirname "$0")/../backups/media

# Create the local backup directory if it doesn't exist
if [ ! -d "$LOCAL_BACKUP_PATH" ]; then
  echo 'Creating the media backup directory'
  mkdir "$LOCAL_BACKUP_PATH"
fi

if [ -d "$LOCAL_BACKUP_PATH" ]; then
  # Backup media folder using tar
  echo 'Backing up media folder...'
  docker-compose exec back tar -zcvf $CONTAINER_BACKUP_PATH/"$DATE".tar.gz "$APPLICATION_PATH"

  # Clean the backup directory, saving only the last 3 backups
  echo 'Cleaning old media backup'
  cd "$LOCAL_BACKUP_PATH"; (ls -t|head -n 3;ls)|sort|uniq -u|xargs rm

  echo 'Save successful!'
else
  echo "Media save path doesn't exit"
  echo 'Media has not been saved'
  exit 1
fi