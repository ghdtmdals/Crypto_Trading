FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-devel

COPY install_lib.sh /app/install_lib.sh

RUN chmod +x /app/install_lib.sh

RUN /app/install_lib.sh

COPY set_env.sh /app/set_env.sh

RUN chmod +x /app/set_env.sh

RUN /app/set_env.sh