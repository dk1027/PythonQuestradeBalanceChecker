#!/bin/bash
# Creates an AWS deployment package
# Copies contents of src and site-packages directories to build/staging/src
# Zip everything up to build/output/package.zip
set -e
echo "Using Profile ${AWS_PROFILE}"
BUILD_DIR=`pwd`
STAGING="${BUILD_DIR}/staging"
OUT_DIR="${BUILD_DIR}/output"
STAGE_SRC="$STAGING/src"
ROOT_DIR=$(dirname "${BUILD_DIR}")
LAMBDA_PACKAGE_NAME="package"

build(){
  echo 'Building deployment package'
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
  zip -r "${OUT_DIR}/${LAMBDA_PACKAGE_NAME}" *

  echo 'Cleaning up...'
  deactivate
  cd $BUILD_DIR
  rm -rf $STAGING
  echo 'Finished'
}

add(){
  echo "Adding ${1}"
  cd ${BUILD_DIR}/../src
  zip -rv ${OUT_DIR}/${LAMBDA_PACKAGE_NAME}.zip ${1}
}

deploy(){
  echo "Deploying Cloudformation stack ${1}"
  aws cloudformation deploy --template-file QuestradeCFTemplate --stack-name ${1} --capabilities CAPABILITY_IAM
}

upload_lambda(){
  echo 'Uploading Lambda'
  aws lambda update-function-code --function-name ${1} --zip-file fileb://${OUT_DIR}/${2}
}

clean(){
  echo "Deleting stack ${1}"
  aws cloudformation delete-stack --stack-name ${1}
}

if [[ $1 == 'build' ]]; then
  build
elif [[ $1 == 'deploy' ]]; then
  if [[ $* == *--only-cf* ]]; then
    echo "Only deploy cloud formation"
    deploy Questrade
  elif [[ $* == *--only-upload* ]]; then
    echo "Only upload lambda package"
    upload_lambda QuestradeBalanceCheck ${LAMBDA_PACKAGE_NAME}.zip
  else
    deploy Questrade
    upload_lambda QuestradeBalanceCheck ${LAMBDA_PACKAGE_NAME}.zip
  fi
  echo 'Finished'
elif [[ $1 == 'clean' ]]; then
  clean Questrade
elif [[ $1 == 'add' ]]; then
  add $2
else
  echo 'Unknown command'
fi
