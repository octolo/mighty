echo "Remove old version"
rm -f ngrok-stable-linux-amd64.tgz
rm -f ngrok

echo "Installation"
echo "1. download ngrok-stable-linux-amd64.tgz"
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.tgz

echo "2. uncompress ngrok-stable-linux-amd64.tgz"
tar zxvf ngrok-stable-linux-amd64.tgz

echo "Usage"
echo "1. Create an account on ngrok.com"
echo "2. Valid your email, it's mandatory to use ngrok"
echo "3. Get your token and do : "
echo "./ngrok authtoken {token}"
echo "4. Start ngrok"
echo "./ngrok http {port django (8000)}"
echo "5. Use the ngrok URL"
echo "Forwarding ... http://***.ngrok.io -> http://localhost:8000"
