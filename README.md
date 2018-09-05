# README #

Docker -- Nginx | Flask | MongoDB | Redis

## Getting Started ##

### Install Docker ###
```
# Uninstall old versions
  $ sudo apt-get remove docker docker-engine

# Recommended extra packages for Trusty 14.04
  $ sudo apt-get update
  $ sudo apt-get install \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual

# Install Docker
  $ sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
  $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  $ sudo apt-key fingerprint 0EBFCD88
  $ sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
  $ sudo apt-get update
  $ sudo apt-get install docker-ce
  $ sudo docker run hello-world

  $ sudo groupadd docker
  $ sudo usermod -aG docker $USER

  # Log out and log back in so that your group membership is re-evaluated.

# Install Docker Compose
  $ sudo curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
  $ sudo chmod +x /usr/local/bin/docker-compose
```

### Start Docker Compose ###
```
$ cd docker-demo-microservice
$ docker-compose up
```

### Stop Docker Compose ###
```
$ docker-compose down
```