# srvbeat


## Install on clients

```
apt -qq update
apt -qq install git python3-pip -y
pip3 $verbosity install git+https://github.com/openbitlab/srvbeat.git@main#egg=srvbeat --exists-action w --ignore-installed 
```

And put this line on /etc/crontab:

```
* * * * * /usr/bin/srvbeat-client name host port >/dev/null 2>&1
```
