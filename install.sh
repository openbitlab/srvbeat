name=$(hostname)
branch="master"
verbosity="-q"

install() {
    echo "[*] Installing beat server..."
    install_beat
    echo "[+] Installed beat!"
    echo "[*] Installing beat service..."
    install_service "/usr/local/bin/srvbeat"
    echo "[+] Installed beat service!"
}

print_help () {
    echo "Usage: install [options...]
 -n  --name <name> monitor name [default is the server hostname]
     --branch <name> name of the branch to use for the installation [default is master]
 -t  --telegram <chat_id> <token> telegram chat options (id and token) where the alerts will be sent [required]
 -v  --verbose enable verbose installation"
}

install_beat () {
    config_file="/etc/srvbeat.conf"
    apt -qq update
    apt -qq install git python3-pip -y
    systemctl stop srvbeat.service
    rm -rf /etc/srvbeat.conf
    rm -rf /etc/systemd/system/srvbeat.service
    pip3 $verbosity install git+https://github.com/openbitlab/srvbeat.git@$branch#egg=srvbeat --exists-action w --ignore-installed 
    wget $verbosity https://raw.githubusercontent.com/openbitlab/srvbeat/$branch/conf/srvbeat.conf -O $config_file ## TODO add args to change service name
    sed -i -e "s/^apiToken =.*/apiToken = \"$api_token\"/" $config_file
    sed -i -e "s/^chatId =.*/chatId = [\"$chat_id\"]/" $config_file
    sed -i -e "s/^name =.*/name = $name/" $config_file
}

install_service () {
    wget -q https://raw.githubusercontent.com/openbitlab/srvbeat/$branch/conf/srvbeat.service -O /etc/systemd/system/srvbeat.service ## TODO add args to change service name
    sed -i -e "s,^ExecStart=.*,ExecStart=$1,g" /etc/systemd/system/srvbeat.service
    systemctl daemon-reload 
    systemctl start srvbeat
    systemctl enable srvbeat
}

POSITIONAL_ARGS=()


while [[ $# -gt 0 ]]; do
case $1 in
    -n|--name)
        if [[ -z $2 ]]
        then
            print_help
            exit 1
        else
            name="$2"
        fi
        shift # past argument
        shift # past value
    ;;
    -v|--verbose)
        verbosity=""
        shift # past argument
    ;;
    --branch)
        if [[ -z $2 ]]
        then
            print_help
            exit 1
        else
            branch="$2"
        fi
        shift # past argument
        shift # past value
    ;;
    -t|--telegram)
        if [[ -z $2 || -z $3 ]]
        then
            print_help
            exit 1
        else
	        chat_id="$2"
            api_token="$3"
        fi
        shift # past argument
        shift # past value
        shift # past value
    ;;
    -*|--*)
        echo "Unknown option $1"
        print_help
        exit 1
    ;;
    *)
        POSITIONAL_ARGS+=("$1") # save positional arg
        shift # past argument
    ;;
esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [[ -z $chat_id || -z $api_token || -z $service ]]
then
    print_help
    exit 1
fi

install
