## requirements: nslookup

from http.server import BaseHTTPRequestHandler, HTTPServer
import pandas as pd
import subprocess, psutil, datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask

SERVER_IP = '217.160.147.188'
HOST_USERNAME = 'root'

def get_time_info(timestamp):

    date1 = datetime.datetime.fromtimestamp(timestamp) # yyyy, mm, dd, HH, MM
    date2 = datetime.datetime.now()

    # Calculate the difference
    diff = date2 - date1

    # Extract the difference in days, hours, and minutes
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds // 60) % 60

    # Generate a human-readable string
    output = ""
    if days > 0:
        output += f"{days} days, "
    elif hours > 0:
        output += f"{hours} hours, "
    elif minutes > 0:
        output += f"{minutes} minutes"
    else:
        output += 'Now'
        return output

    # Remove the trailing comma and space
    output = output.rstrip(", ") + ' ago.'

    return output

def get_dns_addr(ip_address):
    dns = subprocess.getoutput("nslookup "+ip_address+" | awk '/name/ {print $4}'")
    if dns == '':
        return ip_address
    else:
        return dns

def get_urls():

    output = subprocess.getoutput("netstat -lntp | awk 'NR>2{print $4,$7}' |  grep -E '127.0.0.1:' | grep sshd | sort -n")

    if output == '':
        dictionary={"Date":[], "SSH Command":[], "Host": [], "URLs":[]}
        return pd.DataFrame(dictionary) 
    
    port2pid = {i.split(' ')[0].split(':')[1]: i.split(' ')[1].split('/')[0] for i in output.split('\n')}
    port2pid = {i:j for i,j in port2pid.items() if not (i in ['22', '8000'])}
    port2pid = {i:j for i,j in port2pid.items() if int(i)<20000}
    ports = [i for i in port2pid.keys() ]

    server_ips = [subprocess.getoutput("netstat -lntpa | grep "+pid+" | grep ESTABLISHED | awk '{print $5}'") for pid in port2pid.values()]
    server_ips = [[j.split(':')[0] for j in i.split('\n') if j.split(':')[0] not in ['0.0.0.0','127.0.0.1']][0] for i in server_ips]
    server_ips = [get_dns_addr(ip_address) for ip_address in server_ips]

    host_dict = {port_i:ip_i for ip_i, port_i in zip(server_ips, ports)}
    

    datetimes  = [psutil.Process(int(subprocess.getoutput('fuser '+str(i)+'/tcp').split(' ')[-1])).create_time() for i in ports]
    ports = [j for i,j in sorted(zip(datetimes, ports), reverse=True)]
    hosts = [host_dict[i] for i in ports]

    if output != '':    
        urls = ['http://localhost:'+i for i in ports]
    else:
        urls = []

    sshs=['autossh -M 20000 -f -N  -L '+i+':localhost:'+i+' -N '+HOST_USERNAME+'@'+SERVER_IP for i in ports]
    
    ips=[i for i in urls]

    dictionary={"Date":[get_time_info(int(i))for i in sorted(datetimes, reverse=True)],"SSH Command":sshs, "Host":hosts, "URLs":ips}
    df=pd.DataFrame(dictionary)

    return df

def get_public_urls():

    output = subprocess.getoutput("netstat -lntp | awk 'NR>2{print $4,$7}' |  grep -E '0.0.0.0:' | grep sshd | sort -n")

    if output == '':
        dictionary={"Date":[], "SSH Command":[], "Hosts":[],"URLs":[]}
        return pd.DataFrame(dictionary) 
    
    port2pid = {i.split(' ')[0].split(':')[1]: i.split(' ')[1].split('/')[0] for i in output.split('\n')}
    port2pid = {i:j for i,j in port2pid.items() if not (i in ['22', '8000'])}
    port2pid = {i:j for i,j in port2pid.items() if int(i)<20000}

    ports = [i for i in port2pid.keys()]

    server_ips = [subprocess.getoutput("netstat -lntpa | grep "+pid+" | grep ESTABLISHED | awk '{print $5}'") for pid in port2pid.values()]
    server_ips = [[j.split(':')[0] for j in i.split('\n') if j.split(':')[0] not in ['0.0.0.0','127.0.0.1']][0] for i in server_ips]
    server_ips = [get_dns_addr(ip_address) for ip_address in server_ips]

    host_dict = {port_i:ip_i for ip_i, port_i in zip(server_ips, ports)}
    

    datetimes  = [psutil.Process(int(subprocess.getoutput('fuser '+str(i)+'/tcp').split(' ')[-1])).create_time() for i in ports]
    ports = [j for i,j in sorted(zip(datetimes, ports), reverse=True)]
    hosts = [host_dict[i] for i in ports]

    if output != '':    
        urls = ['http://'+SERVER_IP+':'+i for i in ports]
    else:
        urls = []


    sshs=['---' for i in ports]
    
    ips=[i for i in urls]

    dictionary={"Date":[get_time_info(int(i))for i in sorted(datetimes, reverse=True)], "SSH Command":sshs, "Host":hosts,"URLs":ips}
    df=pd.DataFrame(dictionary)

    return df

def get_html_():

    html_code =  pd.merge(get_urls(), get_public_urls(), how='outer').to_html(index=False, escape=False, render_links=True)

    # HTML template with centering and spaces
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background-color: #1E1E1E;  /* Dark background color */
                color: #FFFFFF;  /* Light text color */
            }}
            table {{
                border-collapse: collapse;
                width: 80%;
                margin-top: 20px;
                margin-bottom: 20px;
                background-color: #2D2D2D;  /* Dark table background color */
            }}
            th, td {{
                border: 1px solid #3E3E3E;  /* Dark border color */
                padding: 8px;
                text-align: left;
                color: #FFFFFF;  /* Light text color */
            }}
            a {{
                color: #3498DB;  /* Blue link color */
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        {html_code}
    </body>
    </html>
    """
    return html_template

kk =  get_urls()
app = Flask(__name__)

@app.route('/')
def index():
    return get_html_()

if __name__ == '__main__':
    app.run('0.0.0.0', 8000)
