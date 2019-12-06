#!/usr/bin/env bash
pip3 install --target ./package moesif_aws_lambda
cd package
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -g function.zip lambda_function.py
