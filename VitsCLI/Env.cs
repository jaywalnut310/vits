namespace VitsCLI;

public static partial class Env {
    public static string OutName(string name) => $"{Path.GetFileNameWithoutExtension(name)}-{Random.Shared.Next()}.wav";

    public static void AutoSetup() {

    }
}
