namespace VitsCLI;

using System.Diagnostics;

public static partial class Env {
    public static string OutName(string name) => $"{Path.GetFileNameWithoutExtension(name)}-{Random.Shared.Next()}.wav";

    public static async Task<bool> TryLoad(string[] args) {
        var p = Process.Start(Environment.ProcessPath!, args.Append("-t"));
        await p.WaitForExitAsync();
        return p.ExitCode == 0;
    }

    public static void AutoSetup() {

    }
}
