$var1 = "[PAYLOAD]"
$var2 = [Convert]::FromBase64String($var1)
$var3 = [Text.Encoding]::ASCII.GetString($var2)
$var3 | Out-File [PATH]