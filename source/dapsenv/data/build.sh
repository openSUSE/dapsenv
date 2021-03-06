#!/bin/bash
BUILD_LOG="/tmp/build_log"
STATUS_FILE="/tmp/build_status"
DAPS_OPTIONS=""
FORMAT=$2
FORMAT_FOLDER=""

if [ "$FORMAT" = "single_html" ]; then
  DAPS_OPTIONS="--single"
  FORMAT="html"
  FORMAT_FOLDER="single-html"
else
  FORMAT_FOLDER=$2
fi

DAPS_CMD="daps -vv -d /tmp/build/$4/$1 $FORMAT $DAPS_OPTIONS"
daps -vv -d /tmp/build/$4/$1 $FORMAT $DAPS_OPTIONS &> $BUILD_LOG

if [ $? -eq 0 ]; then
  source /tmp/build/$4/$1

  ARCHIVE_NAME="documentation_$2.tar"
  BUILD_DIR_NAME=$(expr "$1" : '^DC\-\(.*\)$')
  if [ "$ROOTID" = "" ]; then
    BUILD_DIR_PATH="$3/build/$BUILD_DIR_NAME/$FORMAT_FOLDER/$BUILD_DIR_NAME"
  else
    BUILD_DIR_PATH="$3/build/$BUILD_DIR_NAME/$FORMAT_FOLDER/$ROOTID"
  fi

  if [ "$FORMAT" = "pdf" ]; then
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
  if [ ! -z "$ROOTID" ]; then
    XSLTPROCPARAM="--xinclude --stringparam rootid $ROOTID"
  fi

  PRODUCT=$(xsltproc $XSLTPROCPARAM /tmp/productname.xsl $3/build/.profiled/*/$MAIN)
  PRODUCT_NUMBER=$(xsltproc $XSLTPROCPARAM /tmp/productnumber.xsl $3/build/.profiled/*/$MAIN)
  GUIDE=$(xsltproc $XSLTPROCPARAM /tmp/guidename.xsl $3/build/.profiled/*/$MAIN)

  # create doc_info.json
  echo "{ \"product\": \"$PRODUCT\", \"productnumber\": \"$PRODUCT_NUMBER\", \"guide\": \"$GUIDE\", \"dapscmd\": \"$DAPS_CMD\" }" > /tmp/doc_info.json

  echo "success" > $STATUS_FILE
  exit 0
fi

echo "{ \"dapscmd\": \"$DAPS_CMD\" }" > /tmp/doc_info.json
echo "error" > $STATUS_FILE
