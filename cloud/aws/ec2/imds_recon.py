#!/usr/bin/env python3
import requests

IMDS_BASE = "http://169.254.169.254/latest"
HEADERS = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}

# Mapping of IMDS paths and attacker value
paths = {
    "/meta-data/iam/security-credentials/": "❗ IAM Role name (access to AWS APIs if role exists)",
    "/user-data": "📜 Full cloud-init script (possible secrets, IPs, commands)",
    "/meta-data/network/interfaces/macs/": "🌐 MAC address and subnets (network layout)",
    "/meta-data/placement/availability-zone": "🗺️ Availability zone (region recon)",
    "/meta-data/public-ipv4": "🌍 Public IP of EC2 (target host info)",
    "/meta-data/local-ipv4": "🔒 Private IP inside VPC (internal pivoting)",
    "/meta-data/hostname": "🖥️ EC2 hostname (for spoofing or OSINT)",
    "/meta-data/tags/instance": "🏷️ Instance tags (env, project, team, secrets!)",
    "/meta-data/public-keys/": "🔑 SSH public keys (admin access path)",
}

def get_token():
    try:
        r = requests.put(f"{IMDS_BASE}/api/token", headers=HEADERS, timeout=2)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Could not get IMDSv2 token: {e}")
        return None

def query_metadata(token, path):
    url = f"{IMDS_BASE}{path}"
    try:
        r = requests.get(url, headers={"X-aws-ec2-metadata-token": token}, timeout=2)
        if r.status_code == 200:
            return r.text.strip()
        elif r.status_code == 404:
            return None
        else:
            return f"[Error {r.status_code}]"
    except Exception as e:
        return f"[!] Request failed: {e}"

def main():
    print("=== 🕵️ IMDSv2 Recon Report ===")
    token = get_token()
    if not token:
        print("[-] IMDSv2 not available or blocked.")
        return

    for path, purpose in paths.items():
        print(f"\n[*] Path: {path}\n    Purpose: {purpose}")
        result = query_metadata(token, path)
        if result:
            if len(result) > 300:
                print("    Result: [truncated large content]")
            else:
                print(f"    Result:\n{result}")
        else:
            print("    Result: Not available or empty.")

if __name__ == "__main__":
    main()
    
"""
python3 imds_recon.py 
=== 🕵️ IMDSv2 Recon Report ===

[*] Path: /meta-data/iam/security-credentials/
    Purpose: ❗ IAM Role name (access to AWS APIs if role exists)
    Result: Not available or empty.

[*] Path: /user-data
    Purpose: 📜 Full cloud-init script (possible secrets, IPs, commands)
    Result: [truncated large content]

[*] Path: /meta-data/network/interfaces/macs/
    Purpose: 🌐 MAC address and subnets (network layout)
    Result:
06:06:06:06:06:06/

[*] Path: /meta-data/placement/availability-zone
    Purpose: 🗺️ Availability zone (region recon)
    Result:
eu-west-1a

[*] Path: /meta-data/public-ipv4
    Purpose: 🌍 Public IP of EC2 (target host info)
    Result:
54.54.54.54

[*] Path: /meta-data/local-ipv4
    Purpose: 🔒 Private IP inside VPC (internal pivoting)
    Result:
10.10.10.10

[*] Path: /meta-data/hostname
    Purpose: 🖥️ EC2 hostname (for spoofing or OSINT)
    Result:
ip-10-10-10-10.eu-west-1.compute.internal

[*] Path: /meta-data/tags/instance
    Purpose: 🏷️ Instance tags (env, project, team, secrets!)
    Result: Not available or empty.

[*] Path: /meta-data/public-keys/
    Purpose: 🔑 SSH public keys (admin access path)
    Result:
0=keyname-key
"""
