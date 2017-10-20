建立自動執行排程
1. 建立shell script
＄ nano ./job.sh

#!/bin/bash
WORK_PATH="/home/pi/envinfo_client"
cd $WORK_PATH
python /home/pi/envinfo_client/app.py -u http://master

2. 調整job.sh操作權限
＄ chmod +x ./job.sh

3. 建立定時執行排程(注意排程使用者需要能順利執行該程序)
$ crontab -e

*/1 * * * * /home/pi/envinfo_client/job.sh