apt-get update && apt-get install -y sudo

adduser --disabled-password --gecos "" user  \
        && echo 'user:user' | chpasswd \
        && adduser user sudo \
        && echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

sudo apt-get install -y git vim

pip install transformers PyJWT python-dateutil pymysql matplotlib ftfy regex tqdm git+https://github.com/openai/CLIP.git

# pip install git+https://github.com/openai/CLIP.git

conda install -y scikit-learn

AIRFLOW_VERSION=2.10.4
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

airflow users create \
    --username admin \
    --firstname ${AIRFLOW_FIRSTNAME} \
    --lastname ${AIRFLOW_LASTNAME} \
    --role Admin \
    --password ${AIRFLOW_PASSWORD} \
    --email ${AIRFLOW_EMAIL}