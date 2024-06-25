#!/bin/bash
VERSION?='latest'
project_root_dir=${PWD}
software_version=`grep -i version ${project_root_dir}/pyproject.toml |awk -F '"' '{print $2}'`
ZIP_NAME="ideas_api__${software_version}_${VERSION}.zip"
zip_file="${project_root_dir}/$ZIP_NAME" ; # save the result file in current working directory

apt-get update -y && apt-get install zip -y
POETRY_VERSION=1.2.0
POETRY_HOME=/opt/poetry
POETRY_VENV=/opt/poetry-venv
POETRY_CACHE_DIR=/opt/.cache
# Add `poetry` to PATH
PATH="${POETRY_VENV}/bin:${PATH}"

# Install poetry separated from system interpreter
python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}
cp pyproject.toml /tmp/
cp poetry.lock /tmp/
cd /tmp
poetry remove boto3
poetry install
poetry_venv_path=`poetry env info --path`
cd ${project_root_dir}
# TODO remove some libraries to reduce size
rm -rf ${zip_file}
venv_dir="${poetry_venv_path}/lib/python3.9/site-packages"
# ensure that if we added new packages, they will also be added to the zip file
cd $venv_dir && zip -r9 "$zip_file" . && cd "$project_root_dir" && zip -g "$zip_file" -r9 'ideas_api/'
# -r means recursive, 9 means: compress better, -g Grow (append to) the specified zip archive, instead of creating a new one.
#zip -g ../lambda.zip -r .


TERRAFORM_ZIP_NAME="terraform_${ZIP_NAME}"
terraform_zip_file="${project_root_dir}/$TERRAFORM_ZIP_NAME" ; # save the result file in current working directory

cd ${project_root_dir}/tf-module/ideas-api
mkdir build
cp ${zip_file} build/ideas_api_lambda_function.zip

cd $project_root_dir/tf-module/ideas-api
zip -9 ${terraform_zip_file} * **/*

echo 'done zipping terraform'
ls -l

rm build/ideas_api_lambda_function.zip
rmdir build
