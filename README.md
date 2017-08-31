# Ricequant-360-Adapter
An adapter subscribing signals from Ricequant and push to 360

Usage:

```bash

docker run -d -it \
    -e RQ360_APPKEY=<your appkey>\
    -e RQ360_360USER=<your 360 username>\
    -e RQ360_360SECRET=<your 360 secret>\
    -e RQ360_RQUSER=<your ricequant username>\
    -e RQ360_RQPASSWORD=<your ricequant password>\
    -e RQ360_RUNID=<your ricequant PT run id>\
    -e RQ360_SMTPUSER=<your SMTP user name>\
    -e RQ360_SMTPPASSWORD=<your SMTP password> \
    --name <container name>\ coxious/ricequant-360-adapter

```