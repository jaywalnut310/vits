namespace VitsCLI;

using CommandLine;

public class Cfg {
    [Option('d', "PyDLL", HelpText = "Specifies the PythonDLL name of the Python3.")]
    public string? PyDLL { get; set; }

    [Option('p', "PyLoc", HelpText = "Specifies the PythonHome location of the Python38.")]
    public string? PyLoc { get; set; }

    [Option('l', "Local", HelpText = "Use Python that is already installed on the system.")]
    public bool Local { get; set; }

    [Option('t', "Test", HelpText = "Try to load Python.")]
    public bool Test { get; set; }

    [Option('r', "Reset", HelpText = "Reset the included Python.")]
    public bool Reset { get; set; }

    [Option('n', "Clean", HelpText = "NoTTS, Only clean the Text.")]
    public bool Clean { get; set; }

    [Option('c', "Config", HelpText = "Model config.json file location.")]
    public string Config { get; set; } = string.Empty;

    [Option('m', "Model", HelpText = "Model pth or pt file location.")]
    public string Model { get; set; } = string.Empty;

    [Option('o', "Output", HelpText = "WAV file output file or directory.")]
    public string? Output { get; set; }

    [Option('s', "Scale", HelpText = "Valid when PTH. Set the voice speed.")]
    public float Scale { get; set; }

    [Value(0, MetaName = "Text", HelpText = "The text to be converted.")]
    public string Text { get; set; } = "吾輩は猫である。名前はまだない";
}
