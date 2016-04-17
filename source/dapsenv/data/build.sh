#!/bin/bash
BUILD_LOG="/tmp/build_log"
STATUS_FILE="/tmp/build_status"

daps -vv -d /tmp/build/$4/$1 $2 &> $BUILD_LOG

if [ $? -eq 0 ]; then
  ARCHIVE_NAME="documentation.tar"
  BUILD_DIR_NAME=$(expr "$1" : '^DC\-\(.*\)$')
  BUILD_DIR_PATH="$3/build/$BUILD_DIR_NAME/$2/$BUILD_DIR_NAME"
  cd $BUILD_DIR_PATH
  tar cfv $ARCHIVE_NAME * > /dev/null
  mv $ARCHIVE_NAME /tmp
  echo "success" > $STATUS_FILE
else
  echo "error" > $STATUS_FILE
fi
