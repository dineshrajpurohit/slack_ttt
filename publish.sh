#!/usr/bin/env bash

cd deployment
ls -altr
rm ttt.zip
zip -r ttt.zip ../* --exclude=../venv/*
cd ../venv/lib/python3.6/site-packages
zip -r9 ../../../../deployment/ttt.zip *
cd ../../../../deployment
aws lambda update-function-code --function-name ttt --zip-file fileb://ttt.zip
cd ..