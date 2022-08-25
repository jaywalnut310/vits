namespace VitsCLI;

using System.Runtime.InteropServices;

public static partial class Env {
    public static string SetPyDLL(string? lib = null) {
        if (string.IsNullOrWhiteSpace(lib))
            lib = RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
                ? "python38.dll"
                : RuntimeInformation.IsOSPlatform(OSPlatform.OSX)
                    ? "libpython3.8.dylib"
                    : "libpython3.8.so";

        Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", lib);
        return lib;
    }
}
