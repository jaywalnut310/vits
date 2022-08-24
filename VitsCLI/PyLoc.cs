namespace VitsCLI;

using System.Diagnostics;
using System.Runtime.InteropServices;
using Python.Runtime;

public static partial class Env {
    public static void SetPyLoc(string? loc = null, string? dll = null) {
        if (!string.IsNullOrWhiteSpace(loc)) {
            PythonEngine.PythonHome = Directory.Exists(loc) ? loc
                : throw new DirectoryNotFoundException("PythonHome Not Exists " + loc);

            Console.WriteLine("Set PythonHome to: " + loc);
        } else if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {

            var path = Environment.GetEnvironmentVariable("PATH")?.Split(';')
                .FirstOrDefault(p => string.IsNullOrWhiteSpace(dll)
                        ? File.Exists(Path.Combine(p, "python3.dll"))
                        : File.Exists(Path.Combine(p, dll)) && File.Exists(Path.Combine(p, "python3.dll")));

            if (!string.IsNullOrEmpty(path)) {
                PythonEngine.PythonHome = path;
                Console.WriteLine("Set PythonHome to: " + path);
            } else {
                _ = Process.Start("explorer", "https://apps.microsoft.com/store/detail/python-38/9MSSZTT1N39L");
                throw new DllNotFoundException(
                    "It looks like you don't have Python3 installed, please install it, or don't set --Local, or use --PyLoc to locate it.");
            }
        }
    }
}
