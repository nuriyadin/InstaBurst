#!/usr/bin/env bash

# configure the repository file
echo "deb http://http.kali.org/kali kali-rolling main contrib non-free" > /etc/apt/sources.list

# update outdated archive-key
wget -q -O - https://archive.kali.org/archive-key.asc | apt-key add

install() {
 # install pip
 apt-get install python-pip python-dev -y
 pip install --upgrade setuptools --user python

 # install Tor && requirements
 apt-get update && apt-get install tor lighttpd php7.0-cgi -y && apt autoremove -y
 pip install -UI -r requirements.txt
}

install
chmod +x ngrok instagram.py
chmod -R 775 web
install
