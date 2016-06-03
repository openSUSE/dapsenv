#!/bin/bash
# Deletes all tmp files what were created by one build-run

cd /tmp
rm -rf build_* *.json
cd /tmp/build/*
rm -rf build
