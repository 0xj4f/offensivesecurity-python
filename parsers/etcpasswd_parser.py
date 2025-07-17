import json
"""
a script to parse /etc/passwd to readable key pair value

offsec:x:1000:1000:offsec,,,:/home/offsec:/bin/bash

[
    {
        "login_name": "offsec",
        "encrypted_password": "x",
        "uid": "1000",
        "gid": "1000",
        "user_info": "offsec,,,",
        "home_directory": "/home/offsec",
        "shell": "/bin/bash"
    }
]

"""
class PasswdParser:
    def __init__(self, passwd_file='/etc/passwd'):
        self.passwd_file = passwd_file
        self.anomalies = []

    def parse(self):
        users = []
        with open(self.passwd_file, 'r') as file:
            for line in file:
                if line.strip():
                    try:
                        user_info = self._parse_line(line.strip())
                        users.append(user_info)
                    except Exception as e:
                        # Store problematic lines as anomalies
                        self.anomalies.append(line.strip())
        return users

    def _parse_line(self, line):
        fields = line.split(':')
        if len(fields) != 7:
            raise ValueError("Malformed line, expecting 7 fields")  

        return {
            "login_name": fields[0],
            "encrypted_password": fields[1],
            "uid": fields[2],
            "gid": fields[3],
            "user_info": fields[4],
            "home_directory": fields[5],
            "shell": fields[6]
        }

    def to_json(self):
        users = self.parse()
        result = {
            "users": users,
            "anomalies": self.anomalies  # Store anomalies here
        }
        return json.dumps(result, indent=4)

if __name__ == '__main__':
    parser = PasswdParser()
    passwd_json = parser.to_json()
    print(passwd_json)
