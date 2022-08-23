namespace VitsCLI;

using CommandLine;

public class Options {
    [Option('d', "PyDLL", Required = false, HelpText = "Specifies the PythonDLL name of the Python3.")]
    public string? PyDLL { get; set; }

    [Option('p', "PyLoc", Required = false, HelpText = "Specifies the PythonHome location of the Python38.")]
    public string? PyLoc { get; set; }

    [Option('n', "Clean", Required = false, HelpText = "NoTTS, Only clean the Text.")]
    public bool Clean { get; set; }

    [Option('c', "Config", Required = true, HelpText = "Model config.json file location.")]
    public string Config { get; set; } = string.Empty;

    [Option('m', "Model", Required = true, HelpText = "Model pth or pt file location.")]
    public string Model { get; set; } = string.Empty;

    [Option('o', "Output", Required = false, HelpText = "WAV file output file or directory.")]
    public string? Output { get; set; }

    [Value(0, MetaName = "Text", Required = false, HelpText = "The text to be converted.")]
    public string Text { get; set; } = "吾輩は猫である。名前はまだない";
}
