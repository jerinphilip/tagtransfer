#!/bin/bash

wget https://github.com/salesforce/localization-xml-mt/archive/refs/heads/master.zip  -O /tmp/sfxml-data.zip
mkdir $1
unzip /tmp/sfxml-data.zip -d $1
