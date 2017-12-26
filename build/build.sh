#!/bin/bash
# Creates an AWS deployment package
# Copies contents of src and site-packages directories to build/staging/src
# Zip everything up to build/output/package.zip
set -e
build(){
  echo 'Building deployment package'
  BUILD_DIR=`pwd`
  STAGING="${BUILD_DIR}/staging"
  OUT_DIR="${BUILD_DIR}/output"
  STAGE_SRC="$STAGING/src"

  ROOT_DIR=$(dirname "${BUILD_DIR}")

  rm -rf $STAGING
  rm -rf $OUT_DIR
  mkdir $STAGING
  mkdir $STAGE_SRC
  mkdir $OUT_DIR

  # # Copy source files
  cp -r "${ROOT_DIR}/src/" $STAGE_SRC
  cp "${ROOT_DIR}/requirements.txt" $STAGING

  # Get pre-built numpy / pandas for running on the AWS Linux AMI
  cd $STAGING
  git clone https://github.com/pbegle/aws-lambda-py3.6-pandas-numpy.git
  cd $STAGE_SRC
  unzip ../aws-lambda-py3.6-pandas-numpy/lambda.zip

  # Create virualenv and install requirements
  cd $BUILD_DIR
  virtualenv -p `which python3` $STAGING
  source $STAGING/bin/activate
  pip install -r "${STAGING}/requirements.txt"
  cp -r "${VIRTUAL_ENV}/lib/python3.6/site-packages/" $STAGE_SRC

  # Create zip file
  cd $STAGE_SRC
  zip -r "${OUT_DIR}/package" *

  echo 'Cleaning up...'
  deactivate
  cd $BUILD_DIR
  rm -rf $STAGING
  echo 'Finished'
}

deploy(){
  echo 'Deploying to AWS'
}

if [[ $1 == 'build' ]]; then
  build
elif [[ $1 == 'deploy' ]]; then
  deploy
else
  echo 'Unknown command'
fi
  #statements
#
