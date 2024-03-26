set -e


while true
do
    echo loop
    IFS=$'\n'
    for ip in $(nmap -n 192.168.12.1/24 -p 8266 -oG - | awk '/Up$/{print $2}' | sed '/192\.168\.12\.1$/d')
    do
        if grep $ip updated_bots; then
            continue
        fi
        echo $ip
        python upload_fs.py $ip
        if [ $? -eq 0 ]; then
            echo $ip >> updated_bots
        fi
        # python remote_selftest.py $ip
    done
    # sleep 5
done
