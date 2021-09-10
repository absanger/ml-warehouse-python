#!/bin/sh

# Setup mysql server
apt update
apt install -y mysql-server


# Install test requirements
pip3 install -r requirements.txt -r test-requirements.txt

pytest --it