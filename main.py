import argparse
import requests
import time
import hmac
import hashlib
import base64
import json

class FeiShuRobot:
    def __init__(self, robot_id, secret) -> None:
        self.robot_id = robot_id
        self.secret = secret

    def gen_sign(self):
        # Concatenate timestamp and secret
        timestamp = int(round(time.time()))
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

        # Process the result via base64
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return str(timestamp), str(sign)

    def send_text(self, text):
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
                print("INFO: Our text is sent successfully!")
            else:
                print("ERROR: Failed to send text! code: %s, message: %s" % (json_parser["code"], json_parser["msg"]))

            return response.text
        except Exception as e:
            print("发送飞书失败:", e)

if __name__ == '__main__':
    # Parse the input arguments
    parser = argparse.ArgumentParser(description='Run this script to launch a Feishu robot to monitor FPGA status')
    parser.add_argument('-i', '--id', type=str, help='The ID of Feishu robot', required=True)
    parser.add_argument('-s', '--secret', type=str, help='The secret key of Feishu robot', required=True)

    args = parser.parse_args()
    robot_id = args.id
    secret = args.secret

    # Initialize the Feishu robot
    feishu = FeiShuRobot(robot_id, secret)
    feishu.send_text("Hello Feishu!")
