import argparse
import requests
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime
import paramiko

class FeiShuRobot:
    def __init__(self, robot_id, secret, fpga_dict) -> None:
        self.robot_id = robot_id
        self.secret = secret
        self.fpga_dict = fpga_dict

    def gen_sign(self):
        # Concatenate timestamp and secret
        timestamp = int(round(time.time()))
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

        # Process the result via base64
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return str(timestamp), str(sign)

    def send_text(self, text):
        current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{self.robot_id}"
            headers = {"Content-Type": "text/plain"}

            timestamp, sign = self.gen_sign()
            data = {
                        "timestamp": timestamp,
                        "sign": sign,
                        "msg_type": "text",
                        "content": {
                            "text": text
                        }
                    }
            response = requests.post(url, headers=headers, json=data)

            # Check whether we send this message successfully
            json_parser = json.loads(response.text)
            if json_parser["code"] == 0:
                print("[%s] INFO: Our text is sent successfully!" % current_time_str)
            else:
                print("[%s] ERROR: Failed to send text! code: %s, message: %s" % (
                    current_time_str, json_parser["code"], json_parser["msg"]))
        except Exception as e:
            print("[%s] ERROR: Failed to send text due to the following exception:\n\t" % current_time_str, e)

    def get_fpga_status_table(self):
        fpga_status_list = []
        monitor_cmd_list = ["minicom", "pcie-util"]
        ssh_command = "ps -o ruser=userForLongName -e -o pid,ppid,c,stime,tty,time,cmd | grep -E \"%s\" | grep -v \"grep\" | awk \'{print $1}\'" % ('|'.join(monitor_cmd_list))

        for name, value in self.fpga_dict.items():
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(hostname=value['ip'], port=value['port'], username=value['user'], timeout=5)
                stdin, stdout, stderr = ssh.exec_command(ssh_command)
                user_occupy_fpga = stdout.read().decode()[:-1]
                if user_occupy_fpga != '':
                    fpga_status_list.append("%s | %s" % (name, user_occupy_fpga))
                else:
                    fpga_status_list.append("%s | %s" % (name, "---"))
            except Exception as e:
                fpga_status_list.append("%s | %s" % (name, "Unreachable"))
                print("[%s] ERROR: exception occurs when connect %s: " %
                      (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), value['ip']), e)
            ssh.close()

        fpga_status_table = "FPGA Status List\n" + '\n'.join(fpga_status_list)

        return fpga_status_table

if __name__ == '__main__':
    # Parse the input arguments
    parser = argparse.ArgumentParser(description='Run this script to launch a Feishu robot to monitor FPGA status')
    parser.add_argument('-i', '--id', type=str, help='The ID of Feishu robot', required=True)
    parser.add_argument('-s', '--secret', type=str, help='The secret key of Feishu robot', required=True)
    parser.add_argument('-f', '--fpga', type=str, help='The path of fpga JSON file', required=True)

    args = parser.parse_args()
    robot_id = args.id
    secret = args.secret
    with open(args.fpga, "r") as f:
        fpga_dict = json.load(f)

    # Initialize the Feishu robot
    feishu = FeiShuRobot(robot_id, secret, fpga_dict)

    # Check FPGA status every 5 mins
    last_fpga_status = ""
    while True:
        fpga_status_table = feishu.get_fpga_status_table()

        if fpga_status_table != last_fpga_status:
            last_fpga_status = fpga_status_table
            feishu.send_text(fpga_status_table)
        else:
            print("[%s] INFO: FPGA status stays the same, skip sending message!" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        time.sleep(300)
