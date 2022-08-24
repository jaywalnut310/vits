using System.Globalization;
using CommandLine;
using VitsCLI;

Parser.Default.ParseArguments<Cfg>(args)
    .WithParsed(x => {
        if (x.Local)
            Env.SetPyLoc(x.PyLoc, Env.SetPyDLL(x.PyDLL));
        else
            Env.AutoSetup();

        if (x.Test) {
            new Vits(args, false).Dispose();
            return;
        }

        var py = new Vits(args);
        var cleaned = py.Clean(x.Text);

        if (x.Clean) Environment.Exit(0);

        var file = Env.OutName(x.Config);

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
