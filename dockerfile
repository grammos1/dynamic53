FROM ubuntu:latest
RUN apt update
RUN apt install -y python3 python3-pip git
RUN git clone https://github.com/pyRammos/dynamic53.git
WORKDIR dynamic53
RUN pip3 install -r requirements
RUN echo "#!/bin/bash" > start.sh
RUN echo "cp /settings/dynamic53.cfg ." > start.sh
RUN echo "python3 dynamic53.py --profile WAN1" >> start.sh
ENTRYPOINT ["sh", "start.sh"]