#!/bin/bash

### /etc/environment
> /etc/environment

while IFS='=' read -r -d '' key value; do
    echo "$key=$value" >> /etc/environment
done < <(env -0)

### /etc/ssh/sshd_config -> 루트 로그인, 비밀번호 없이 로그인 활성화
sudo passwd root -d ### root계정 비밀번호 삭제

sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

sed -i 's/^#PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config
sed -i 's/^PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config