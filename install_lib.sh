apt-get update && apt-get install -y sudo

adduser --disabled-password --gecos "" user  \
        && echo 'user:user' | chpasswd \
        && adduser user sudo \
        && echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

sudo apt-get install -y git

pip install transformers PyJWT python-dateutil pymysql matplotlib ftfy regex tqdm

pip install git+https://github.com/openai/CLIP.git

conda install -y scikit-learn

### 컨테이너 종료 방지
# /bin/bash