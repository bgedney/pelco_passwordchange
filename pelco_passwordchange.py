#!/usr/bin/python
import requests
import argparse
import re
import ast
import socket

parser = argparse.ArgumentParser(description='')

parser.add_argument('--current', help='Enter the current Password')
parser.add_argument('--ip', help='Enter the ip address of the camera')
parser.add_argument('--new', help='Enter the new Password')
parser.add_argument('--user', help='Enter the user', default = 'admin')
parser.add_argument('--txt', help='Enter a Text document with each IP on a new line')

args = parser.parse_args()

print args
current = args.current
new = args.new
user = args.user
ip = args.ip
text_file = args.txt

ip_list = []
if args.ip:
    ip_list.append(ip)
if text_file:
    with open(text_file, "r") as IP_file:
        ip_file_txt = IP_file.readlines()
    ip_file_list = []
    for item in ip_file_txt:
        stripped = item.rstrip("\r\n")
        ip_file_list.append(stripped)
    for ipFileList in ip_file_list:
        pattern = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        if pattern.match(ipFileList):
            ip_list.append(str(ipFileList))
total = 0
for h in ip_list:
    total += 1
success = 0
failed = 0
loop = 0
failed_ips = []
for host in ip_list: 
    loop += 1
    print '******************  Host ' + str(loop) + ' of ' + str(total) + '  ******************'
    print "Changing password for " + host
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host,80))
    if result == 0:
        check_host = 'http://' + host + '/auth/validate'
        check_request = requests.get(check_host)
        if check_request.status_code == 200:
            print 'Camera Type: Sarix'
            session = requests.Session()
            login_url = 'http://' + host + '/auth/validate'
            login_response = session.post(login_url, data = {'username': user, 'password': current}, allow_redirects=False )
            passwordChange_url = 'http://' + host + '/auth/change_password'
            change_response = session.post(passwordChange_url, data = {'username': '', 'old_password': current, 'new_password': new, 'password_confirm': new}, allow_redirects=False)
            if change_response.status_code == 302:
                print "Changed Password"
                success += 1
            elif change_response.status_code == 200:
                print "There Was an error changing the password for: " + host
                failed += 1
                failed_ips.append(host)
            logout_url = 'http://' + host + '/auth/logout'
            logout_request = session.get(logout_url)
            if logout_request.status_code == 302:
                print host + " Session Terminated"
        elif check_request.status_code == 404:
            print 'Camera Type: SpectraIV-IP PTZ'
            session = requests.Session()
            login_url = 'http://' + host + '/content/login.php'
            login_response = session.post(login_url, data = {'username': user, 'password': current}, allow_redirects=False)
            passwordChange_url = 'http://' + host + '/view/profile'
            change_response = session.post(passwordChange_url, data = {'passwd': new, 'pconf': new}, allow_redirects=False)
            if '<span class="message-text">Updated Profile</span>' in change_response.text:
                print "Changed Password"
                success += 1
            else:
                print "There Was an error changing the password for: " + host
                failed += 1
                failed_ips.append(host)
            logout_url = 'http://' + host + '/content/logout.php'
            logout_request = session.get(logout_url)
            if logout_request.status_code == 302:
                print host + " Session Terminated"
    else:
        failed += 1
        failed_ips.append(host)

print '***************************************************'
print ""
print "++++++++++++++++++++  Summary  ++++++++++++++++++++"
print str(success) + " of " + str(total) + " hosts successfully updated."
print str(failed) + " hosts FAILED"
print "+++++++++++++++++++++++++++++++++++++++++++++++++++"
print ""
if len(failed_ips) > 0:
    print "=================   FAILED HOSTS   ================"
    for h in failed_ips:
        print str(h)
