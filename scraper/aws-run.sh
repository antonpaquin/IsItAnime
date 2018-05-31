ROOT_DIR="/home/anton/Programming/AnimeDetect++/scraper"
SSH_KEY="/home/anton/.ssh/Nimitz-120518.pem"

echo "Checking SSH security group..."
if aws ec2 describe-security-groups --group-names "GlobalSSH" > /dev/null; then
    echo "Security group already exists"
else
    aws ec2 create-security-group \
        --group-name "GlobalSSH" \
        --description "Allow 22 traffic in"
    
    aws ec2 authorize-security-group-ingress \
        --group-name "GlobalSSH" \
        --protocol "tcp" \
        --port 22 \
        --cidr "0.0.0.0/0"

    echo "Security group \"GlobalSSH\" created"
fi

echo "Starting instance..."
INSTANCE_ID=$(\
aws ec2 run-instances \
    --image-id "ami-f973ab84" \
    --key-name "Nimitz-12.05.18" \
    --security-groups "GlobalSSH" \
    --instance-type "t2.small" \
    --placement "AvailabilityZone=us-east-1b" \
    --count 1 \
| jq -r .Instances[0].InstanceId \
)
echo "Spawned instance: $INSTANCE_ID"

pushd "$ROOT_DIR"


if [ -f "$ROOT_DIR/transfer.zip" ]; then
    rm "$ROOT_DIR/transfer.zip"
    echo "Removed old zipfile"
fi

tar -czvf \
    "isitanime_scrapy.tar.gz" \
    "isitanime_scrapy"

echo "Zipping sources..."
zip \
    -r "$ROOT_DIR/transfer.zip" \
    --junk-paths \
    "$ROOT_DIR/isitanime_scrapy.tar.gz" \
    "$ROOT_DIR/manhole.diff" \
    "$ROOT_DIR/http.diff" 

pushd "$HOME"
zip \
    -r "$ROOT_DIR/transfer.zip" \
    -g \
    ".aws/" 
popd

# Wait for the instance to start -- it takes a while to boot up
echo "Waiting for instance to start..."
aws ec2 wait instance-running \
    --instance-ids "$INSTANCE_ID"
echo "Started"

# Get the public IP of the instance so we can SSH to it
echo "Fetching public ip..."
INSTANCE_IP=$(\
aws ec2 describe-instances \
    --instance-id "$INSTANCE_ID" \
    --query "Reservations[].Instances[].PublicIpAddress" \
    --output=text
)
echo "Found ip: $INSTANCE_IP"
cat > ssh_aws <<EOF
host awsec2
    HostName $INSTANCE_IP
    port 22
    User ec2-user
    IdentityFile ~/.ssh/Nimitz-120518.pem
EOF

# Continuously try to SSH into the instance and do nothing
# We move on when it works
echo "Attempting to SSH into instance..."
while ! ssh -i "$SSH_KEY" -oStrictHostKeyChecking=no ec2-user@$INSTANCE_IP true; do
    echo "SSH failed, retrying..."
    sleep 1
done
echo "Success"

# Send over the transfer zip
echo "Transferring zipped sources..."
scp \
    -i "$SSH_KEY" \
    "$ROOT_DIR/transfer.zip" \
    ec2-user@$INSTANCE_IP:~/transfer.zip
echo "Transfer complete"

# Primary SSH -- all this runs on the server
echo "Beginning server commands..."
ssh -i "$SSH_KEY" ec2-user@$INSTANCE_IP <<ENDSSH
    unzip transfer.zip
    rm transfer.zip

    sudo yum groupinstall -y \
        development

    sudo yum install -y \
        python3 \
        python3-devel \
        libxslt-devel \
        libxml2-devel \
        libffi-devel

    sudo pip3 install \
        scrapy \
        scrapyd \
        scrapyd-client \
        spiderkeeper \
        boto3 \
        requests

    tar -xzvf \
        isitanime_scrapy.tar.gz

    pushd "isitanime_scrapy"
    python3 setup.py bdist_egg
    cp dist/isitanime_scrapy-1.0-py3.7.egg \$HOME/isitanime.egg
    popd

    sudo patch /usr/local/lib64/python3.7/site-packages/twisted/conch/manhole.py manhole.diff
    rm manhole.diff
    sudo patch /usr/local/lib64/python3.7/site-packages/twisted/web/http.py http.diff
    rm http.diff
ENDSSH
