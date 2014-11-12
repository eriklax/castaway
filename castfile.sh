#!/bin/sh

set -e
cd "`dirname "$1"`"
file="`pwd`"/$(basename "$1")
id="`curl -X POST -d \"$file\" http://127.0.0.1:8000/playlist 2> /dev/null`"
id=`echo "$id" | sed -e 's/{"id": //' -e 's/}//'`
curl http://127.0.0.1:8000/skip-to/$id
