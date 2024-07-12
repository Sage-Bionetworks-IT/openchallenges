FROM mariadb:10.9.3

RUN apt update && apt install -y \
  iputils-ping \
  jq \
  curl \
  dnsutils \
  nmap \
  net-tools \
  netcat

COPY docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
COPY docker-healthcheck /usr/local/bin/
COPY my.cnf /etc/mysql/

HEALTHCHECK CMD ["docker-healthcheck"]
