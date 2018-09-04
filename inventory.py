import os, sys , time
import paramiko
import telnetlib
import mysql.connector

def main():
    user = 'win'
    password = 'win'
    en_pass = 'win'
    ope = open('C:\\Users\\Thanawin\\Desktop\\testip\\iptest.txt','r')
    print ('--- Start ---')
    keep = ope.read().split('\n')
    ope.close()
    '''result=[]'''
        
    for i in keep:
        print (i)
        '''result.append(telnet(i,user,password))'''
        call(i,user,password, en_pass)

    # cwd = os.getcwd()
    # print ("Path Output " + (cwd))
    print ('--- End ---')
    input("Press enter to exit...")


def call(Host,username,passwd, en_pass):
    cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='ticket')
    cursor = cnx.cursor()

    port = 22
    switch = ""
    outdata = ""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(Host ,port, username=username , password=passwd, look_for_keys=False ,allow_agent=False)
        console = ssh.invoke_shell()
        console.keep_this = ssh

        print ("Login")
        """evet enable password"""
        console.send('en' + '\n')
        console.send(en_pass + '\n')

        console.send('terminal length 0' + '\n')
        # console.send('sh ver' + '\n')
        # time.sleep(1)
        # console.send('sh int des' + '\n')
        # time.sleep(1)
        # console.send('sh int status' + '\n')
        # time.sleep(1)
        # console.send('sh cdp nei' + '\n')
        # time.sleep(1)
        console.send('sh inven' + '\n')
        time.sleep(1)
        console.send('terminal length 24' + '\n')
        outdata = console.recv(204800)
        ssh.close()
        print ("Finish")

    except (IOError , ValueError):
        pass
    count_name_switch = 0
    for line in outdata.decode("utf-8").split('\n'):
        if('#' in line):
            if (count_name_switch == 0):
                keep = line.split('#')
                switch = keep[0]
                add_switch = ("INSERT INTO switch_inven "
               "(hostname, ip, type) "
               "VALUES (%s, %s, %s)")
                data_switch = (switch, Host, "Core")
                cursor.execute(add_switch, data_switch)
                cnx.commit()
                count_name_switch += 1
            else:
                pass
        elif ("NAME: " in line):
            temp1 = line.split(',')
            name = temp1[0].split(' ')
            name = name[1]
            temp2 = temp1[1].split(' ')
            DESCR = temp2[2]
        elif("PID: " in line):
            temp1 = line.split(',')
            sn = temp1[2].split(' ')
            sn = sn[2]
            temp2 = temp1[0].split(' ')
            pid = temp2[1]
            add_switch = ("INSERT INTO module_inven "
               "(name, descr, pid, serial, hostname_id) "
               "VALUES (%s, %s, %s, %s, %s)")
            data_switch = (name, DESCR, pid, sn, switch)
            cursor.execute(add_switch, data_switch)
            cnx.commit()

            print("Hostname :" + switch)
            print("NAME :" + name)
            print("DESCR :" + DESCR)
            print("PID : " + pid)
            print("SN : " + sn)
            
    # if not os.path.exists(switch):
    #    os.makedirs(switch, mode=0o777)
    #    print ("Okey")
    # elif os.path.exists(switch):
    #    print ("None Okey")
    save = open("test3560.txt",'w')
    save.write(outdata.decode("utf-8") + '\n')                    
    save.close()

    cnx.commit()
    cursor.close()
    cnx.close()


main()