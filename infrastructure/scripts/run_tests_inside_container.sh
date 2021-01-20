#!/bin/bash
set -e

TESTS_LOCATION=$1
REPORT_FILE=$2

pytest $TESTS_LOCATION --junitxml=$REPORT_FILE
