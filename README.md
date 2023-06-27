# Install

```bash
CODE_SERVER_VERSION=4.14.1
git clone https://github.com/ankanbhunia/vscode-remote
cd vscode-remote
chmod +x vscode host host.public
curl -fL https://github.com/coder/code-server/releases/download/v$CODE_SERVER_VERSION/code-server-$CODE_SERVER_VERSION-linux-amd64.tar.gz > code-server.tar.gz
tar -xvf code-server.tar.gz
```

# Commands

1. ```./vscode``` -> run vscode on a random port.
2.  ```./vscode 8080``` -> run vscode on port 8080.
3. ```sbatch <file.sh>``` -> run vscode using sbatch. 
4. ```bash sbatch-autoconnect <file.sh>``` -> automatically reconnects vscode instance.
5. ```./host 8080``` -> port forwarding on port 8080
6. ```./host.public 8080``` -> share port 8080 publicly (not recommended)
7. ```./host --login``` -> login to save public key of your local machine to the server.
8. ```./host --active``` -> shows active ports on the server
9. ```./host --history``` -> echo $host.log

Check ```host.log``` or slurm log file for SSH command. The output should look like following
```bash
Sharing port 7867 press Ctrl+Z to exit
Run this command on your local machine:
    ssh -L 8080:localhost:8080 -N root@217.160.147.188
Open http://localhost:8080 in a browser. Port forwarding successful.
```
# Steps
1. ```sbatch <file.sh>``` or  ```./vscode``` (on server side)
2. ```ssh -L <port>:localhost:<port> -N root@217.160.147.188``` (on local machine; check ```host.log``` for actual SSH command.)
3. Open http://localhost:port in a browser

N.B. ```./host --login``` when running for the first time.
