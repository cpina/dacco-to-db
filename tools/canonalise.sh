#!/bin/bash

xmllint --format "$1" | xmlstarlet c14n

#cat "$1" | xml_pp -s none | xmlstarlet c14n
