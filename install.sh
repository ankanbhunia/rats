CODE_SERVER_VERSION=4.14.1

if [ "$(uname)" == "Linux" ]; then
    sysx="linux"
elif [ "$(uname)" == "Darwin" ]; then
    sysx="macos"
else
    echo "Unsupported operating system."
    exit 1
fi
server_name=$1
git clone https://github.com/ankanbhunia/rats
cd rats
echo "$server_name" > "server_name.txt"
chmod +x vscode host host.public ftp killall
curl -fL https://github.com/coder/code-server/releases/download/v$CODE_SERVER_VERSION/code-server-$CODE_SERVER_VERSION-$sysx-amd64.tar.gz > code-server.tar.gz
tar -xvf code-server.tar.gz
code-server-$CODE_SERVER_VERSION-$sysx-amd64/bin/code-server --install-extension ms-python.python --force  --extensions-dir vscode-extensions_dir
