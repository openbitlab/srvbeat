# srvbeat

## Install

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/srvbeat/master/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -n <name> <optional_flags>
```

## Install on clients

```
apt -qq update
apt -qq install git python3-pip -y
pip3 $verbosity install git+https://github.com/openbitlab/srvbeat.git@master#egg=srvbeat --exists-action w --ignore-installed 
```

And put this line on /etc/crontab:

```
* * * * * /usr/bin/srvbeat-client name host port >/dev/null 2>&1
```
