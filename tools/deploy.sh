#!/bin/bash
echo 'DEPLOYING'
export REPO=hasadna/reportit-scripts
. tools/prepare_github.sh
git checkout -b __deploy
find src -name script.json | xargs git add
git status
git commit -m "Auto update of json scripts"
git push -v origin __deploy:master
