# Container for Flask API
FROM ubuntu:18.04

# set work directory
WORKDIR /root

# copy project
COPY . .

# install dependencies
RUN apt-get update && \
    apt-get install -y ssh sudo && \
    mkdir /root/.ssh

# copy over keyfile
COPY epic-interview.pub /root/.ssh/authorized_keys

# make sshd happy
RUN chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/authorized_keys && \
    mkdir -p /var/run/sshd

EXPOSE 22

# entrypoint
CMD ["/usr/sbin/sshd", "-D"]