namespace VitsCLI;

using System.CommandLine;
using System.IO;
using System.Runtime.InteropServices;
using Python.Runtime;

internal class Program {
    private static bool noTTS;

    public static async Task<int> Main(string[] args) {
        var root = new RootCommand("CraftVits CLI");

        {
            var pyLib = "python38.dll";

            if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
                pyLib = "libpython3.8.so";
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
                pyLib = "libpython3.8.dylib";

            Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pyLib);
            Console.WriteLine("PythonDLL name is: " + pyLib);
        }

        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            var path = Environment.GetEnvironmentVariable("PATH")?.Split(';')
                .Where(p => !p.Contains("WindowsApps"))
                .FirstOrDefault(p => File.Exists(Path.Combine(p, "python.exe")));

            if (!string.IsNullOrEmpty(path)) {
                PythonEngine.PythonHome = path;
                Console.WriteLine("Set PythonHome to: " + path);
            } else {
                Console.Error.WriteLine("It looks like you don't have Python38 installed, please install it, or use --PyLoc to locate it.");
                _ = System.Diagnostics.Process.Start("https://apps.microsoft.com/store/detail/python-38/9MSSZTT1N39L");
                return -1;
            }
        }

        {
            var pyLoc = new Option<string?>("--PyLoc", "Specifies the PythonHome location of the Python38.");

            root.AddOption(pyLoc);
            root.SetHandler(dic => PythonEngine.PythonHome = Directory.Exists(dic)
                ? PythonEngine.PythonHome = dic
                : throw new DirectoryNotFoundException("PythonHome Not Exists " + dic), pyLoc);
        }

        {
            var pyDLL = new Option<string?>("--PyDLL" ,"Specifies the PythonDLL name of the Python38.");

            root.AddOption(pyDLL);
            root.SetHandler(name => Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", name), pyDLL);
        }

        {
            var clean = new Option<bool>("--Clean", "NoTTS, Only clean the Text");

            root.AddOption(clean);
            root.SetHandler(b => noTTS = b, clean);
        }

        {
            var ja = new Argument<string>("ja", () => "吾輩は猫である。名前はまだない", "The Japanese text to be converted.");

            root.Add(ja);
            root.SetHandler(str => {
                var py = new Vits();
                var cleaned = py.Clean(str);
                py.PT(new("E:/CaChe/NimiSora.json"), new("E:/CaChe/NimiSora.pt"), cleaned, new("E:/CaChe/NimiSora.wav"));
            }, ja);
        }

        return await root.InvokeAsync(args);
    }
}
