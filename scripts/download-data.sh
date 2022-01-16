#!/bin/bash

DATA_DIR="$PWD/data"

ARCHIVE="$DATA_DIR/sfxml-data.zip"

# Create folder if not exists
mkdir -p $DATA_DIR

# Get archive from internet
wget --continue --quiet --show-progress \
    https://github.com/salesforce/localization-xml-mt/archive/refs/heads/master.zip  \
    -O $ARCHIVE

# Unzip to data-dir
unzip -o $ARCHIVE -d $DATA_DIR


