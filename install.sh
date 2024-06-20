#!/bin/bash

sudo apt update
#sudo apt upgrade -y

sudo apt install -y git cmake build-essential

git clone https://github.com/axiomatic-systems/Bento4.git

cd Bento4

mkdir cmakebuild
cd cmakebuild
cmake -DCMAKE_BUILD_TYPE=Release ..
make

sudo cp mp4decrypt /usr/local/bin/

# Check if copying was successful
if [ -f /usr/local/bin/mp4decrypt ]; then
    echo "mp4decrypt successfully copied to /usr/local/bin/"
else
    echo "Error copying mp4decrypt to /usr/local/bin/"
    exit 1
fi

# Delete Bento4 directory
cd ./../..
rm -rf Bento4

# Completion message
echo "mp4decrypt installed successfully, and Bento4 directory removed."

python3 -m pip install requests