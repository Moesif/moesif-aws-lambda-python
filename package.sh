#!/usr/bin/env bash
rm -rf package build dist
pip3 uninstall moesif_aws_lambda
pip3 install --target ./package -r requirements.txt 
cd package
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -g function.zip lambda_function.py moesif_aws_lambda/*
