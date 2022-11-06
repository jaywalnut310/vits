namespace VitsCLI;

using System.Diagnostics;
using System.Runtime.InteropServices;
using Python.Runtime;

public static partial class Env {
    public static void SetPyLoc(string? loc = null, string? dll = null) {
        if (!string.IsNullOrWhiteSpace(loc)) {
            var path = Directory.Exists(loc)
                ? loc
                : throw new DirectoryNotFoundException("PythonHome Not Exists " + loc);

            var raw = Environment.GetEnvironmentVariable("PATH")?.TrimEnd(';');
            Environment.SetEnvironmentVariable("PATH", string.IsNullOrEmpty(raw) ? path : $"{raw};{path}", EnvironmentVariableTarget.Process);
            Environment.SetEnvironmentVariable("PYTHONHOME", path, EnvironmentVariableTarget.Process);
            PythonEngine.PythonHome = path;

        } else if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            var path = Environment.GetEnvironmentVariable("PATH")?.Split(';')
                .FirstOrDefault(p => string.IsNullOrWhiteSpace(dll)
                    ? File.Exists(Path.Combine(p, "python3.dll"))
                    : File.Exists(Path.Combine(p, dll)) && File.Exists(Path.Combine(p, "python3.dll")));

            if (!string.IsNullOrEmpty(path))
                PythonEngine.PythonHome = path;
            else {
                _ = Process.Start("explorer", "https://apps.microsoft.com/store/detail/python-38/9MSSZTT1N39L");
                throw new DllNotFoundException(
                    "It looks like you don't have Python38 installed, please install it, or don't set --Local, or use --PyLoc to locate it.");
            }
        }
    }
}
