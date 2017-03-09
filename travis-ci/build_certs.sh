#!/bin/bash
# The 'good' cert
openssl req -new -x509  -keyout travis-ci/cakey.pem -out travis-ci/cacert.pem -days 365 -passout pass:fakepassword -subj "/C=US/ST=WA/L=Seattle/O=FakeTestingOrg/CN=fakeca.travis-ci"
openssl req -out travis-ci/server_req.pem -new -newkey rsa:4096 -nodes -keyout travis-ci/server_key.pem -subj "/C=US/ST=WA/L=Seattle/O=FakeTestingOrg/CN=localhost" 
openssl x509 -req -days 365 -passin pass:fakepassword -in travis-ci/server_req.pem -CA travis-ci/cacert.pem -CAkey travis-ci/cakey.pem -out travis-ci/server-cert.pem -CAcreateserial


# The 'bad' cert that our tests can't validate
openssl req -new -x509  -keyout travis-ci/cakey2.pem -out travis-ci/cacert2.pem -days 365 -passout pass:fakepassword -subj "/C=US/ST=WA/L=Seattle/O=FakeTestingOrg/CN=fakeca.travis-ci2"
openssl req -out travis-ci/server_req2.pem -new -newkey rsa:4096 -nodes -keyout travis-ci/server_key2.pem -subj "/C=US/ST=WA/L=Seattle/O=FakeTestingOrg/CN=localhost"
openssl x509 -req -days 365 -passin pass:fakepassword -in travis-ci/server_req2.pem -CA travis-ci/cacert2.pem -CAkey travis-ci/cakey2.pem -out travis-ci/server-cert2.pem -CAcreateserial
