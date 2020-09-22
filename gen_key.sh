#!/usr/bin/env bash
set -e

FILE="epic-interview"

if [[ -f "$FILE.pem" && -f "$FILE.pub" ]]; then
    echo "$FILE.pem and $FILE.pub exists, not generating new keys."
else 
    echo "$FILE.pem or $FILE.pub do not exist."
    # cleanup if partial delete
    rm "$FILE.pem" && rm "$FILE.pub"
    echo "Generating new private/public keys."
    ssh-keygen -b 2048 -t rsa -f 'epic-interview' -q -N ""
    mv 'epic-interview' 'epic-interview.pem'
fi

echo "Done."