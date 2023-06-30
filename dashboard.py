import dash, subprocess, psutil, datetime
import dash_html_components as html
import requests, dash_table
from bs4 import BeautifulSoup
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, callback, Input, Output
import lxml.html

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

def get_title(url):
    try:
        # response = requests.get(url)
        # soup = BeautifulSoup(response.content, "html.parser")
        # title = soup.find("title").text
        t = lxml.html.parse(url)
        return t.find(".//title").text
    except:
        return 'N/A'

def get_urls():

    output = subprocess.getoutput("netstat -lnt | awk 'NR>2{print $4}' | grep -E '127.0.0.1:' | sed 's/.*://' | sort -n | uniq")


    if output == '':
        dictionary={"Date":[], "SSH Command":[], "Hosts":[],"URLs":[]}
        return pd.DataFrame(dictionary) 
        
    l = subprocess.getoutput("lsof -iTCP  | grep ' 10u ' | grep LISTEN | grep IPv4 | awk '{print $2,$9}'")
    l2 = {i.split(' ')[0]:i.split(' ')[-1].split(':')[-1] for i in l.split('\n')}
    h = subprocess.getoutput("lsof -iTCP  | grep ' 3u ' | grep ESTABLISHED | grep IPv4 | awk '{print $2,$9}'")
    h2 = {i.split(' ')[0]:i.split('->')[-1].split(':')[0] for i in h.split('\n')}
    g = {l2[i]:h2[i] for i in l2}
    
    ports = [i for i in output.split('\n') if i not in ['22', '8000']]
    datetimes  = [psutil.Process(int(subprocess.getoutput('fuser '+str(i)+'/tcp').split(' ')[-1])).create_time() for i in ports]
    ports = [j for i,j in sorted(zip(datetimes,ports), reverse=True)]
    hosts = [g[i] for i in ports]

    if output != '':    
        urls = ['http://localhost:'+i for i in ports]
    else:
        urls = []

    #urls = [{'IP':'http://217.160.147.188:'+i, 'URL':'http://app.lonelycoder.live:'+i, 'Title':get_title('http://217.160.147.188:'+i)} for i in urls]

    #title=[get_title(i) for i in urls]
    sshs=['ssh -L '+i+':localhost:'+i+' -N root@217.160.147.188' for i in ports]
    
    ips=[html.A(html.P(i),href=i) for i in urls]

    dictionary={"Date":[get_time_info(int(i))for i in sorted(datetimes, reverse=True)],"SSH Command":sshs, "Hosts":hosts, "URLs":ips}
    df=pd.DataFrame(dictionary)

    return df

def get_public_urls():
    
    output = subprocess.getoutput("netstat -lnt | awk 'NR>2{print $4}' | grep -E '0.0.0.0:' | sed 's/.*://' | sort -n | uniq")
    if output == '':
        dictionary={"Date":[], "Hosts":[], "URLs":[]}
        return pd.DataFrame(dictionary) 
        
    l = subprocess.getoutput("lsof -iTCP  | grep ' 10u ' | grep LISTEN | awk '{print $2,$9}'")
    l2 = {i.split(' ')[0]:i.split(' ')[-1].split(':')[-1] for i in l.split('\n')}
    h = subprocess.getoutput("lsof -iTCP  | grep ' 3u ' | grep ESTABLISHED | awk '{print $2,$9}'")
    h2 = {i.split(' ')[0]:i.split('->')[-1].split(':')[0] for i in h.split('\n')}
    g = {l2[i]:h2[i] for i in l2}
    
    ports = [i for i in output.split('\n') if i not in ['22', '8000']]
    datetimes  = [psutil.Process(int(subprocess.getoutput('fuser '+str(i)+'/tcp').split(' ')[-1])).create_time() for i in ports]
    ports = [j for i,j in sorted(zip(datetimes,ports), reverse=True)]
    hosts = [g[i] for i in ports]

    if output != '':    
        urls = ['http://217.160.147.188:'+i for i in ports]
    else:
        urls = []

    ips=[html.A(html.P(i),href=i) for i in urls]

    dictionary={"Date":[get_time_info(int(i))for i in sorted(datetimes, reverse=True)],"Hosts":hosts,  "URLs":ips}
    df=pd.DataFrame(dictionary)

    return df

app = dash.Dash(external_stylesheets=[dbc.themes.CYBORG])
app.title = 'Dashboard'
app.layout = html.Div([html.Div(style = {'width': '70%'}, id='main'
), html.Br(),html.Button('Refresh', id='trigger', style={'display':'none'})])

@callback(
    Output('main', 'children'),
    [Input('trigger', 'n_clicks')])
def display_page(relative_pathname):
    return html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Private Tunnels"), close_button=False),
                dbc.ModalBody(dbc.Table.from_dataframe(get_urls(), striped=True, bordered=True, hover=True)),
                dbc.ModalHeader(dbc.ModalTitle("Public Tunnels"), close_button=False),
                dbc.ModalBody(dbc.Table.from_dataframe(get_public_urls(), striped=True, bordered=True, hover=True)),
            ],
            id="modal-centered",
            centered=True,
            is_open=True,
            size="xl",
        ),
        
    ]
)

if __name__ == '__main__':
    app.run_server('0.0.0.0', 8000)
