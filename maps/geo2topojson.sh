#!/bin/bash

jsonfile=$1
topojson -o $jsonfile.topo $jsonfile
