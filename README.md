# srvbeat

## Install

```bash 
curl -s https://raw.githubusercontent.com/openbitlab/srvbeat/master/install.sh | bash -s -- -t <tg_chat_id> <tg_token> -n <name> <optional_flags>
```

Use -k to keep current configuration.
Use --etcd <this_ip> to set the ip of local machine as endpoint of etcd


### Configure call via twilio

Edit /etc/srvbeat.conf and fill the following fields:

```
[twilio]
accountSid =
authToken = 
from = 
to = 
```

and turn callEnabled to true.

Srvbeat will perform a voice call to [to] after [callAfter] minutes of downtime.


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
Note: If using with etcd setup, a cronjob is needed for each node in the cluster
