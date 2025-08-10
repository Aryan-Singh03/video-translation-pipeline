import os
import subprocess
import urllib.request
import zipfile

def set_up():
    subprocess.run(["pip3", "install", "-U", "pip", "setuptools", "wheel"])
    subprocess.run(["git", "clone", "https://github.com/myshell-ai/OpenVoice.git"])
    
    # install requirements
    subprocess.run(["pip3", "install", "-r", "requirements.txt"])
    
    # download checkpoint file
    checkpoint_url = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip"
    checkpoint_path = "OpenVoice/checkpoints_v2_0417.zip"
    
    print("downloading checkpoints")
    urllib.request.urlretrieve(checkpoint_url, checkpoint_path)
    
    # extract  zip file
    print("extracting checkpoints")
    with zipfile.ZipFile(checkpoint_path, 'r') as zip_ref:
        zip_ref.extractall("OpenVoice/")
    
    # remove zip file
    os.remove(checkpoint_path)

set_up()