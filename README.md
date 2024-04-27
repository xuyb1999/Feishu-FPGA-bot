# Feishu FPGA Bot

## Introduction

This bot is designed to check the occupancy status of an FPGA board and, if necessary, send notifications through Feishu.

## Usage

To use this bot, execute the following command in your terminal:

```shell
python main.py -i <Feishu Bot ID> -s <Feishu Bot Secret> -f <Path to FPGA JSON file>
```

* <b>Feishu Bot ID/Secret</b>: To obtain your Feishu Bot ID and Secret, please refer to the [official Feishu documentation](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot).
* <b>SSH Configuration</b>: Before running the script, ensure that your SSH user is configured to allow password-less access.
