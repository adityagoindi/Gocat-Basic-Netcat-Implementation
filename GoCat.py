#Gocat:Netcat Implementation
#Author:Aditya Goindi

#imports
    import socket
    import sys
    import getopt
    import threading
    import subprocess

#Global Variables
    listen  = False
    command = False
    execute = ''
    upload = ''
    target = ''
    port   = 0


#=======================================Client_Function=======================================================
    def client_func(buffer):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((target,port))

            if len(buffer):
                client.send(buffer)

            while True:

                recv_len = 1
                response = ''
                while recv_len:
                    data = client.recv(4096)
                    recv_len = len(data)
                    response += data

                    if recv_len < 4096:
                        break
                print(response)

                buffer  = input("")
                buffer += "\n"

        except:
            print ("Exception!")
            client.close()


#======================================Server_Function========================================================
    def server_func():
        global target
        global port

        if not len(target):
            target = "0.0.0.0"

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((target, port))
        server.listen(5)
        while True:
            client_sock, addr = server.accept()

            client_thread = threading.Thread(target=client_handler,args=(client_sock,))
            client_thread.start()

#========================================Handling_Client======================================
    def client_handler(client_sock):
        global execute
        global command
        global upload

        if len(upload):
            file_buffer = ""

            while True:
                data = client_sock.recv(1024)

                if not data:
                    break
                else:
                    file_buffer += data

            try:
                file_descriptor = open(upload,"wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                client_sock.send("Successfully saved file to %s\r\n" % upload)
            except:
                client_sock.send("Failed to save file to %s\r\n" % upload)



        if len(execute):
            output = run_command(execute)
            client_sock.send(output)

        if command:

            while True:
                client_sock.send("<GoCat:#> ")
                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += client_sock.recv(1024)

                response = run_command(cmd_buffer)
                client_sock.send(response)

    #===================================Banner=============================================================
    def banner():
        print ("GoCat: Netcat Replacement")
        print
        print ("Usage: gocat.py -t target -p port")
        print ("-l --listen                - listen on [host]:[port]")
        print ("-e --execute=file_to_run   - execute file upon receiving a connection")
        print ("-c --command               - initialize a command shell")
        print ("-u --upload=destination    - upload a file and write to [destination]")
        print
        print
        print ("Examples: ")
        print ("gocat.py -t 192.168.0.10 -p 1234 -l -c")
        print ("gocat.py -t 192.168.0.10 -p 1234 -l -u=c:\\target.exe")
        print ("gocat.py -t 192.168.0.10 -p 1234 -l -e=\"cat /etc/passwd\"")
        print ("echo 'ABCDEFGHI' | ./gocat.py -t 192.168.11.12 -p 4444")
        sys.exit(0)


#====================================Running _Remote _Commands================================
    def run_command(command):
        command = command.rstrip()
        try:
            output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
        except:
            output = "Failed to execute command.\r\n"
        return output

#=========================================main=====================================================
    def main():
        global listen
        global execute
        global command
        global upload
        global target
        global port

        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu', ['help', 'listen', 'execute', 'target', 'port', 'command', 'upload'])
        except getopt.GetoptError as err:
            print (str(err))
            banner()

        for o,a in opts:

            if o in ['h', '--help']:
                banner()
            elif o in ['l', '--listen']:
                listen = True
            elif o in ['e', '--execute']:
                execute = a
            elif o in ['t', '--target']:
                listen = True
            elif o in ['p', '--port']:
                port = a
            elif o in ['c', '--command']:
                command = a
            elif o in ['u', '--upload']:
                upload = a
            else:
                print("Invalid Option.")



        #not listening
            if not listen and len(target) and port>0 :
                buffer = sys.stdin.read()
                client_func(buffer)

            if listen:
                server_func()

#==============================================================================================


    main()
