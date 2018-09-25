import os, sys , time
import paramiko
import telnetlib
import mysql.connector

def main():
    user = "sakrapee"
    password = "sakrapee41"
    en_pass = 'win'
    ope = open('C:\\Users\\Thanawin\\Desktop\\python_network_script\\Inventory\\testinvencore.txt','r')
    print ("--- Start ---")
    keep = ope.read().split('\n')
    ope.close()
    '''result=[]'''
        
    for i in keep:
        print (i)
        '''result.append(telnet(i,user,password))'''
        call(i,user,password, en_pass)

    # cwd = os.getcwd()
    # print ("Path Output " + (cwd))
    print ("--- End ---")


def call(Host,username,passwd, en_pass):
    cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='ticket')
    cursor = cnx.cursor()
    check_login = 0
    port = 22
    switch = ""
    outdata = ""
    name = ""
    DESCR = ""
    pid = ""
    sn = ""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(Host ,port, username=username , password=passwd, look_for_keys=False ,allow_agent=False)
        console = ssh.invoke_shell()
        console.keep_this = ssh
        check_login += 1
        print ("Login")
        """evet enable password"""
        # console.send('en' + '\n')
        # console.send(en_pass + '\n')

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
    if check_login == 1:
        count_name_switch = 0
        for line in outdata.decode("utf-8").split('\n'):
            if('#' in line):
                if (count_name_switch == 0):
                    keep = line.split('#')
                    switch = keep[0]

                    query = ("SELECT * FROM switch_inven "
                    "WHERE hostname = %s")
                    cursor.execute(query, (switch, ))
                    rows = cursor.fetchall()
                    count_switch_inven = 0
                    for i in rows:
                        count_switch_inven += 1
                    if (count_switch_inven > 0):
                        sql_Delete_query = "Delete from switch_inven where hostname = %s"
                        del_switch = (switch, )
                        cursor.execute(sql_Delete_query, del_switch)
                        print("delete " + switch + " in database")
                    type_switch = switch[-4] + switch[-3]
                    count_name_switch += 1
                else:
                    pass
            elif ("NAME: " in line):
                temp1 = line.split(',')
                name = temp1[0].split('"')
                name = name[1]
                temp2 = temp1[1].split('"')
                DESCR = temp2[1]
            elif("PID: " in line):
                temp1 = line.split(',')
                sn = temp1[2].split(' ')
                sn = sn[2]
                temp2 = temp1[0].split(' ')
                pid = temp2[1]
                add_switch = ("INSERT INTO switch_inven "
                   "(hostname, ip, type, name, descr, pid, serial) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                data_switch = (switch, Host, type_switch, name, DESCR, pid, sn)
                cursor.execute(add_switch, data_switch)
                cnx.commit()
                print("add "+ pid + " in database")
    
            
    # if not os.path.exists(switch):
    #    os.makedirs(switch, mode=0o777)
    #    print ("Okey")
    # elif os.path.exists(switch):
    #    print ("None Okey")

    cnx.commit()
    cursor.close()
    cnx.close()


main()