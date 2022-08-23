namespace VitsCLI;

using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using CommandLine;
using Python.Runtime;

internal class Program {
    public static void Main(string[] args) =>
        Parser.Default.ParseArguments<Options>(args)
            .WithParsed(x => {
                {
                    var pyLib = x.PyDLL;

                    if (string.IsNullOrWhiteSpace(pyLib))
                        pyLib = RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
                            ? "python38.dll"
                            : RuntimeInformation.IsOSPlatform(OSPlatform.OSX)
                                ? "libpython3.8.dylib"
                                : "libpython3.8.so";

                    Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pyLib);
                    Console.WriteLine("Set PythonDLL name to: " + pyLib);
                }

                if (!string.IsNullOrWhiteSpace(x.PyLoc)) {
                    PythonEngine.PythonHome = Directory.Exists(x.PyLoc) ? x.PyLoc
                        : throw new DirectoryNotFoundException("PythonHome Not Exists " + x.PyLoc);

                    Console.WriteLine("Set PythonHome to: " + x.PyLoc);
                } else if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {

                    var path = Environment.GetEnvironmentVariable("PATH")?.Split(';')
                        .FirstOrDefault(p => File.Exists(Path.Combine(p, "python3.dll")));

                    if (!string.IsNullOrEmpty(path)) {
                        PythonEngine.PythonHome = path;
                        Console.WriteLine("Set PythonHome to: " + path);
                    } else {
                        Console.Error.WriteLine(
                            "It looks like you don't have Python3 installed, please install it, or use --PyLoc to locate it.");
                        _ = Process.Start("explorer", "https://apps.microsoft.com/store/detail/python-38/9MSSZTT1N39L");
                    }
                }

                var py = new Vits();
                var cleaned = py.Clean(x.Text);

                if (x.Clean) Environment.Exit(0);

                var file = $"{Path.GetFileNameWithoutExtension(x.Config)}-{Random.Shared.Next()}.wav";

                if (string.IsNullOrWhiteSpace(x.Output))
                    x.Output = Path.Combine(AppContext.BaseDirectory, file);

                if (Directory.Exists(x.Output))
                    x.Output = Path.Combine(x.Output, file);

                Console.WriteLine("Save File to " + x.Output);

                if (x.Model.EndsWith(".pth", true, CultureInfo.InvariantCulture)) {
                    py.PTH(x.Config, x.Model, cleaned, x.Output);
                    py.Dispose();
                    return;
                }

                py.PT(x.Config, x.Model, cleaned, x.Output);
                py.Dispose();
            });
}
