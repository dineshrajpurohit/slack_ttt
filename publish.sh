#!/usr/bin/env bash

cd deployment
ls -altr
rm ttt.zip
zip -X -r ttt.zip ../*
aws lambda update-function-code --function-name ttt --zip-file fileb://ttt.zip
cd ..