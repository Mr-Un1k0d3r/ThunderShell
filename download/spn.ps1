$search = New-Object DirectoryServices.DirectorySearcher([ADSI]"")
$search.filter = "(servicePrincipalName=*)"

## You can use this to filter for OU's:
## $results = $search.Findall() | ?{ $_.path -like '*OU=whatever,DC=whatever,DC=whatever*' }
$results = $search.Findall()

foreach( $result in $results ) {
	$userEntry = $result.GetDirectoryEntry()
	Write-host "Object Name = " $userEntry.name -backgroundcolor "yellow" -foregroundcolor "black"
	Write-host "DN      =      "  $userEntry.distinguishedName
	Write-host "Object Cat. = "  $userEntry.objectCategory
	Write-host "servicePrincipalNames"

	$i=1
	foreach( $SPN in $userEntry.servicePrincipalName ) {
		Write-host "SPN(" $i ")   =      " $SPN
		$i+=1
	}
	Write-host ""
}
