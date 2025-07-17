#!/bin/bash

# Dynamic Variables
organization="j4f"
organization_unit="j4flabs"
common_name="j4f root ca"
country="PH"
key_name="j4f_root"
key_size=2048
days_valid=1024

# Generate the CA key
openssl genrsa -out "${key_name}.key" "${key_size}"

# Create the certificate signing request (CSR) and self-signed certificate
openssl req -x509 -new -nodes -key "${key_name}.key" -sha256 -days "${days_valid}" \
    -out "${key_name}.pem" -subj "/C=${country}/O=${organization}/OU=${organization_unit}/CN=${common_name}"

# Convert the PEM certificate to DER format
openssl x509 -outform der -in "${key_name}.pem" -out "${key_name}.crt"

echo "Certificate and key generated: ${key_name}.pem, ${key_name}.key, ${key_name}.crt"

# Certificate and key generated: j4f_root.pem, j4f_root.key, j4f_root.crt