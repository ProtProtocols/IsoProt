
img_name="veitveit/isolabeledprotocol" 
if [ -n "$1" ]; then img_name=$1; fi

# TODO  have an option to override with named parameter
# (my bash skills are not good enough) 
data=`pwd`

# find  first free port 
# There is probably a better way
PORT=`python -c "
import socket, itertools
s = socket.socket()
for port in itertools.count(8888):
    try: s.bind(('', port)); break
    except OSError: continue
print(port)
"` 

# OK, let's hope there are no race conditions as this isn't really atomic

ADRESS="http://localhost:$PORT/" 
echo "using port:" $PORT
echo $ADRESS

# open the adress in the browser (idealy this shold go after docker run)
# it will work, maybe a sec or two for browser to refresh
xdg-open $ADRESS &
docker run -it -p $PORT:8888 -v $data:/data/ $img_name 


