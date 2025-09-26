# RESTART DOCKER SERVER ISSUES

Find and kill redis server
```
sudo kill -9 $(docker inspect -f '{{.State.Pid}}' redis)
```
```
docker rm -f redis
```

Restart Docker
```
sudo systemctl restart docker
```