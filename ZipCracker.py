import os
import shutil
import zipfile
import sys
from threading import Thread
from collections import OrderedDict
import time


def is_zip_encrypted(file_path):
    """
    检查zip文件是否存在伪加密
    """
    with zipfile.ZipFile(file_path) as zf:
        for info in zf.infolist():
            if info.flag_bits & 0x1:
                return True
    return False


def fix_zip_encrypted(file_path):
    """
    修复伪加密的zip文件
    """
    temp_path = file_path + ".tmp"
    with zipfile.ZipFile(file_path) as zf, zipfile.ZipFile(temp_path, "w") as temp_zf:
        for info in zf.infolist():
            if info.flag_bits & 0x1:
                info.flag_bits ^= 0x1  # 清除加密标记
            temp_zf.writestr(info, zf.read(info.filename))
    fix_zip_name = "fix_" + file_path
    try:
        shutil.move(temp_path, fix_zip_name)
    except:
        os.remove(fix_zip_name)
        shutil.move(temp_path, fix_zip_name)
    return fix_zip_name


def crack_password(password, stop):
    global success, cost_time
    try:
        zf = zipfile.ZipFile(zip_file)
        zf.setpassword(password.encode())
        zf.extractall()
        print(f'\n[*]恭喜你！密码破解成功,该压缩包的密码为：{password}')
        success = True
        filenames = zf.namelist()
        print(f"[*]系统已为您自动提取出{len(filenames)}个文件：{filenames}")
        stop[0] = True  # 破解成功，设置 stop 为 True
        os._exit(0)
        return True
    except:
        passwords_cracked = len(tried_passwords)
        avg_cracked = int(passwords_cracked / cost_time)
        remaining_time = time.strftime('%H:%M:%S',
                                       time.gmtime((total_passwords - passwords_cracked) / avg_cracked))
        print("\r[-]当前破解进度：{:.2f}%，剩余时间：{}，当前时速：{}个/s，正在尝试密码:{:<20}".format(
            passwords_cracked / total_passwords * 100, remaining_time, avg_cracked, password),
            end="", flush=True)
    finally:
        cost_time += time.time() - start
    return False


if __name__ == '__main__':
    print("""                          
 ______          ____                _   [*]Hx0战队      
|__  (_)_ __    / ___|_ __ __ _  ___| | _____ _ __ 
  / /| | '_ \  | |   | '__/ _` |/ __| |/ / _ \ '__|
 / /_| | |_) | | |___| | | (_| | (__|   <  __/ |   
/____|_| .__/___\____|_|  \__,_|\___|_|\_\___|_|   
       |_| |_____|                                 
#Coded By Asatomo               Update:2023.07.30
        """)
    if len(sys.argv) == 1:
        print("[*]用法1(内置字典):Python3 Hx0_Zip_Cracker.py YourZipFile.zip \n[*]用法2(自定义字典):Python3 Hx0_Zip_Cracker.py  YourZipFile.zip  YourDict.txt")
        os._exit(0)
    zip_file = sys.argv[1]
    if is_zip_encrypted(zip_file):
        print(f'[!]系统检测到 {zip_file} 是一个加密的ZIP文件')
        zf = zipfile.ZipFile(zip_file)
        try:
            fix_zip_name = fix_zip_encrypted(zip_file)
            zf = zipfile.ZipFile(fix_zip_name)
            zf.testzip()
            zf.extractall()
            filenames = zf.namelist()
            print(
                f"[*]压缩包 {zip_file} 为伪加密，系统已为您生成修复后的压缩包({fix_zip_name})，并自动提取出出{len(filenames)}个文件：{filenames}")
            os._exit(0)
        except Exception as e:
            zf = zipfile.ZipFile(zip_file)
            print(f'[+]压缩包 {zip_file} 不是伪加密，准备尝试暴力破解')
            # 破解加密的zip文件
            password_list = []
            if len(sys.argv) > 2:  # 检查是否指定了自定义字典文件
                dict_file = sys.argv[2]
            else:
                dict_file = 'password_list.txt'
            with open('password_list.txt', 'r') as f:
                password_list += [line.strip() for line in f.readlines()]
            print(f'[+]加载用户字典成功！')
            for length in range(1, 7):
                password_list += [f'{i:0{length}d}' for i in range(10 ** length)]
            print(f'[+]加载0-6位纯数字字典成功！')
            password_list = list(OrderedDict.fromkeys(password_list))
            tried_passwords = []
            total_passwords = len(password_list)
            print(f"[+]当前爆破字典总数:{total_passwords}个")
            print(f"[+]系统开始进行暴力破解······")
            success = False
            cost_time = 0.00001
            stop = [False]  # 用列表存储 stop 变量，使其可以在多个线程间共享
            threads = []
            for password in password_list:
                tried_passwords.append(password)
                if not stop[0]:  # 检查 stop 变量的值，决定是否启动线程
                    start = time.time()
                    t = Thread(target=crack_password, args=[password, stop])
                    threads.append(t)
                    t.start()
            for t in threads:
                t.join()
            if not success:
                print('\n[-]非常抱歉，字典中的所有密码均已尝试，请尝试其他字典或使用更高级的破解方法！')
