#!/bin/bash
BUILD_LOG="/tmp/build_log"
STATUS_FILE="/tmp/build_status"

daps -vv -d /tmp/build/$4/$1 $2 &> $BUILD_LOG

if [ $? -eq 0 ]; then
  source /tmp/build/$4/$1

  ARCHIVE_NAME="documentation.tar"
  BUILD_DIR_NAME=$(expr "$1" : '^DC\-\(.*\)$')
  if [ "$ROOTID" = "" ]; then
    BUILD_DIR_PATH="$3/build/$BUILD_DIR_NAME/$2/$BUILD_DIR_NAME"
  else
    BUILD_DIR_PATH="$3/build/$BUILD_DIR_NAME/$2/$ROOTID"
  fi

  if [ "$2" = "pdf" ]; then
    cd $3/build/$BUILD_DIR_NAME
    tar cfv $ARCHIVE_NAME *.pdf > /dev/null
  else
    cd $BUILD_DIR_PATH
    if [ $? -eq 0 ]; then
      tar cfv $ARCHIVE_NAME * > /dev/null
    fi
  fi

  mv $ARCHIVE_NAME /tmp

  # determine some product information and put it into /tmp/doc_info.json as JSON string
  # this will be used for DAPSEnv
  PRODUCT=$(xmlstarlet sel -t -v '(/*/_:info/_:productname|/*/*/productname)[1]' $3/build/.profiled/*/$MAIN)
  PRODUCT_N=$(xmlstarlet sel -t -v '(/*/_:info/_:productnumber|/*/*/productnumber)[1]' $3/build/.profiled/*/$MAIN)
  #GUIDE=$(xmlstarlet sel -N _=http//docbook.org/ns/docbook -t -v '(/_:*/_:title|/_:*/_:info/_:title|/*/title|/*/*/title)[1]' $3/build/.profiled/*/$MAIN)
  GUIDE=$(xsltproc /tmp/guidename.xsl $3/build/.profiled/*/$MAIN)
  echo "{ \"product\": \"$PRODUCT\", \"productnumber\": \"$PRODUCT_N\", \"guide\": \"$GUIDE\" }" > /tmp/doc_info.json

  echo "success" > $STATUS_FILE
  exit 0
fi

echo "error" > $STATUS_FILE
