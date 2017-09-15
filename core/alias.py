"""
    @author: Mr.Un1k0d3r RingZer0 Team
    @package: core/alias.py
"""
class Alias:
    
    def __init__(self):
        self.alias = {}
        self.alias["powerview"] = ("https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1", "PowerView tool set")
        self.alias["powerup"] = ("https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Privesc/PowerUp.ps1", "PowerUp tool set")
        self.alias["mimikatz"] = ("https://github.com/PowerShellMafia/PowerSploit/raw/master/Exfiltration/Invoke-Mimikatz.ps1", "Invoke-Mimikatz utility")
        self.alias["wmiexec"] = ("https://raw.githubusercontent.com/Mr-Un1k0d3r/RedTeamPowershellScripts/master/scripts/Remote-WmiExecute.ps1", "Remote-WmiExecute utility")
        self.alias["searchevent"] = ("https://github.com/Mr-Un1k0d3r/RedTeamPowershellScripts/blob/master/scripts/Search-EventForUser.ps1", "Search-EventForUser utility")
        self.alias["inveigh"] = ("https://raw.githubusercontent.com/Kevin-Robertson/Inveigh/master/Scripts/Inveigh.ps1", "Invoke-Inveigh utility")
        self.alias["keethief"] = ("https://raw.githubusercontent.com/HarmJ0y/KeeThief/master/PowerShell/KeeThief.ps1", "KeeThief tool set (Get-KeePassDatabaseKey)")
        
        self.custom_alias = {}
        
    def get_alias(self, alias):
        return self.is_alias(alias)
        
    def is_alias(self, alias):
        if self.alias.has_key(alias.lower()):
            return self.alias[alias][0]
        
        if self.custom_alias.has_key(alias.lower()):
            return self.custom_alias[alias]
        
        return alias
    
    def get_all_alias(self):
        return self.alias.keys()
    
    def get_all_custom_alias(self):
        return self.custom_alias.keys()
    
    def get_description(self, alias):
        return self.alias[alias][1]
    
    def get_custom_description(self, alias):
        return self.custom_alias[alias]
    
    def get_customs(self):
        return self.custom_alias
    
    def set_custom(self, key, value):
        self.custom_alias[key] = value
        
    def list_alias(self):
        print "\n\nList of built in alias\n-----------------------\n"
        
        for key in self.get_all_alias():
            print "\t%s%s%s" % (key, " " * (24 - len(key)), self.get_description(key))
        
    def list_custom_alias(self):

        print "\n\nList user defined alias\n-----------------------\n"
        
        for key in self.get_all_custom_alias():
            print "\t%s%s%s" % (key, " " * (24 - len(key)), self.get_custom_description(key))
