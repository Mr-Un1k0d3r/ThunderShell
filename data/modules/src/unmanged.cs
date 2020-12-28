using System;
using System.Text;
using System.Management.Automation;
using System.Collections.ObjectModel;
using System.Management.Automation.Runspaces;

namespace unmanagedps
{
    class Program
    {
        static void Main(string[] args)
        {
            StringBuilder sb = new StringBuilder();
            try
            {
                Runspace rs = RunspaceFactory.CreateRunspace();
                rs.Open();

                RunspaceInvoke ri = new RunspaceInvoke(rs);

                Pipeline pipe = rs.CreatePipeline();
                pipe.Commands.AddScript(Encoding.UTF8.GetString(Convert.FromBase64String(args[0])));
                pipe.Commands.Add("Out-String");
                Collection<PSObject> output = pipe.Invoke();
                rs.Close();
                foreach (PSObject line in output)
                {
                    sb.AppendLine(line.ToString());
                }
                Console.WriteLine(sb.ToString());
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }
    }
}