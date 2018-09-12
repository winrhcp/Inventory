import os, sys , time
import paramiko
import telnetlib
import mysql.connector

def main():
    """Main Function"""
    user = 'sakrapee'
    password = 'sakrapee41'

    ip_client = ""
    for n in sys.argv:
        try:
            ip_client = str(n)
        except Exception as e:
            raise e
    print ("--- Start ---")
    
    '''result=[]'''
        
    core_switch(ip_client, user, password)
    # cwd = os.getcwd()
    # print ("Path Output " + (cwd))
    print ("--- End ---")
    input("Press enter to exit...")

def core_switch(Host,username,passwd):
    """ssh to core switch and get core name, ip core, ip DS, port core to DS"""
    port = 22
    switch = ""
    outdata = ""
    ip_ds = ""
    ip_core = ""
    #filter ip client to core
    check_client = Host.split('.')
    if(len(check_client[1])==2):
        ob = check_client[1]
        ob = ob[0]
        if(ob == "1"):
            ip_core = "10.7.0.1"
        elif(ob == "2"):
            ip_core = "10.7.0.3"
        elif(ob == "3"):
            ip_core = "10.7.0.5"
        else:
            print("NOT FOUND THIS IP")
            return
    else:
        print("NOT FOUND THIS IP")
        return
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_core ,port, username=username , password=passwd, look_for_keys=False ,allow_agent=False)
        console = ssh.invoke_shell()
        console.keep_this = ssh

        print ("Login Core Switch")

        console.send('terminal length 0' + '\n')
        console.send('sh ip route '+ Host + '\n')
        time.sleep(1)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)

        ssh.close()
        

    except (IOError , ValueError):
        return
    count_name_switch = 0
    for line in outdata.decode("utf-8").split('\n'):
        if('#' in line):
            if (count_name_switch == 0):
                keep = line.split('#')
                switch = keep[0]
                count_name_switch += 1
            else:
                pass
        elif('*' in line):
            temp1 = line.split(',')
            ip_ds = temp1[1].split()
            ip_ds = ip_ds[1]
    core_name = switch
    print("Switch Core Name :" + core_name)
    print("IP DS :" + ip_ds)
    print ("Finish Core Switch")
    d_switch(Host, ip_core, ip_ds, core_name, username, passwd)

    # if not os.path.exists(switch):
    #    os.makedirs(switch, mode=0o777)
    #    print ("Okey")
    # elif os.path.exists(switch):
    #    print ("None Okey")
    # save = open('test3560.txt','w')
    # save.write(outdata.decode("utf-8") + '\n')                    
    # save.close()
def d_switch(Host, ip_core, ip_ds, core_name, username, passwd):
    """ssh to distribution switches and get DS name, IP DS, MAC AS, Vlan DS to AS, port DS to AS, IP AS"""
    port = 22
    ds_name = ""
    outdata = ""
    mac_as = ""
    vl_ds_as = ""
    port_ds_as = ""
    ip_as = ""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_ds ,port, username=username , password=passwd, look_for_keys=False ,allow_agent=False)
        console = ssh.invoke_shell()
        console.keep_this = ssh
        
        print ("Login Distribution Switches")

        console.send('terminal length 0' + '\n')
        console.send('sh ip arp | in '+ Host + '\n')
        time.sleep(1)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)
        count_name_switch = 0
        for line in outdata.decode("utf-8").split('\n'):
            if("#" in line):
                if (count_name_switch == 0):
                    keep = line.split('#')
                    ds_name = keep[0]
                    count_name_switch += 1
                else:
                    pass
            elif ("ARPA" in line):
                temp1 = line.split()
                mac_as = temp1[3]
                vl_ds_as = temp1[5]

        console.send('terminal length 0' + '\n')
        console.send('sh mac address-table | in '+ mac_as + '\n')
        time.sleep(2)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)
        for line in outdata.decode("utf-8").split('\n'):
            if("dynamic" in line):
                temp1 = line.split()
                port_ds_as = temp1[4]

        console.send('terminal length 0' + '\n')
        console.send('sh cdp nei '+ port_ds_as + ' detail' + '\n')
        time.sleep(1)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)
        for line in outdata.decode("utf-8").split('\n'):
            if("IP address:" in line):
                temp1 = line.split()
                ip_as = temp1[2]
        ssh.close()
        

    except (IOError , ValueError):
        pass
    print("DS Name :" + ds_name)
    print("IP Core :" + ip_core)
    print("IP DS :" + ip_ds)
    print("MAC Client :" + mac_as)
    print("Vlan DS To AS :" + vl_ds_as)
    print("Port DS To AS : " + port_ds_as)
    print("IP AS : " + ip_as)
    print ("Finish Distribution Switches")
    """Core attribute"""
    core = [core_name, ip_core]
    """DS attribute"""
    ds = [ds_name, ip_ds, vl_ds_as, port_ds_as]

    a_switch(Host, core, ds, username, passwd, mac_as, ip_as)

def a_switch(Host, core, ds, username, passwd, mac_as, ip_as):
    """ssh to Access Switch and get """
    port = 22

    core_name = core[0]
    ip_core = core[1]

    ds_name = ds[0]
    ip_ds = ds[1]
    vl_ds_as = ds[2]
    port_ds_as = ds[3]

    vl_cli = ""
    port_as_client = ""
    as_name = ""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_ds ,port, username=username , password=passwd, look_for_keys=False ,allow_agent=False)
        console = ssh.invoke_shell()
        console.keep_this = ssh
        console.send('ssh -l '+ username + " " + ip_as + '\n')
        time.sleep(1)
        console.send(passwd + '\n')
        print ("Login Access Switch")

        console.send('terminal length 0' + '\n')
        console.send('sh mac add | in '+ mac_as + '\n')
        time.sleep(1)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)
        for line in outdata.decode("utf-8").split('\n'):
            if("#" in line):
                keep = line.split('#')
                as_name = keep[0]
            elif ("DYNAMIC" in line):
                temp1 = line.split()
                port_as_client = temp1[3]
                vl_cli = temp1[0]
        print("Acess Switch Name : " + as_name)
        print("Port Acess Switch to Client : " + port_as_client)
        print("Vlan Client : " + vl_cli)
        ssh.close()
        

    except (IOError , ValueError):
        pass
    print ("Finish Access Switch")

main()