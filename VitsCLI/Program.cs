using CommandLine;
using VitsCLI;

Parser.Default.ParseArguments<Cfg>(args)
    .WithParsed(x => {
        if (x.Reset) {
            Env.AutoSetup(true).Wait();
            Console.WriteLine("已成功重建 Python 运行时");
            return;
        }

        if (x.Local)
            Env.SetPyLoc(x.PyLoc, Env.SetPyDLL(x.PyDLL));
        else
            Env.AutoSetup().Wait();

        if (x.Test) {
            new Vits(args, false).Dispose();
            return;
        }

        var py = new Vits(args);
        var cleaned = py.Clean(x.Text);

        if (x.Clean) {
            py.Dispose();
            return;
        }

        var file = Env.OutName(x.Config);

        if (string.IsNullOrWhiteSpace(x.Output))
            x.Output = Path.Combine(AppContext.BaseDirectory, file);

        if (Directory.Exists(x.Output))
            x.Output = Path.Combine(x.Output, file);

        Console.WriteLine("\nSave File to file://" + x.Output.Replace('\\', '/'));

        py.Do(x, cleaned);
        py.Dispose();
    });
