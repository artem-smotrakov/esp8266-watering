#!/bin/bash

cat ${1} | jq -r .private_key | sed 's/\\n/\n/g' > key.pem

rm -rf key.pem > /dev/null 2>&1
