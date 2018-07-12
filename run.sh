
img_name="veitveit/isolabeledprotocol" 
if [ -n "$1" ]; then img_name=$1; fi

# TODO  have an option to override with named parameter
# (my bash skills are not good enough) 
data=`pwd`

# find  first free port 
# There is probably a better way
PORT=`python -c "
import socket, itertools
from socket import error as socket_error
s = socket.socket()
for port in itertools.count(8888):
    try: s.bind(('', port)); break
    except Exception: continue
print(port)
"` 

# make sure the PORT was found
if [ -z "${PORT}" ]; then
    echo "Error: Failed to find free port."
    exit 1
fi

# create the OUT directory
if [ ! -d "OUT" ]; then
    mkdir OUT

    if [ $? != 0 ]; then
        echo "Error: Failed to create result directory ('OUT')."
        exit 1
    fi
fi

# OK, let's hope there are no race conditions as this isn't really atomic

ADRESS="http://localhost:$PORT/" 
echo "using port:" $PORT
echo $ADRESS

# get root access
echo "Launching docker requires root access..."
sudo echo ""

# Launch the webbrowser with a 10 second delay
( sleep 10 ; xdg-open $ADRESS) &

# Launch the docker image
sudo docker run -it -p $PORT:${PORT} -v $data:/data/ $img_name jupyter notebook --ip=0.0.0.0 --port=${PORT} --no-browser
