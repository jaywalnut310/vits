namespace VitsCLI;

using Python.Runtime;

public class Vits : IDisposable {
    private readonly Py.GILState gil;
    private dynamic? clr;
    private dynamic? vits;

    public Vits() {
        PythonEngine.Initialize();
        this.gil = Py.GIL();

        dynamic sys = Py.Import("sys");
        sys.path.append(AppContext.BaseDirectory);
    }

    public string Clean(string str) {
        this.clr ??= Py.Import("cleaner");

        var res = this.clr.japanese_cleaner(str);
        Console.WriteLine(res);
        return res;
    }

    public void PT(FileInfo config, FileInfo model, string cleaned, FileInfo output) {
        this.vits ??= Py.Import("craft_vits");
        this.vits.pt(config.FullName, model.FullName, cleaned, output.FullName);
    }

    public void PTH(FileInfo config, FileInfo model, string cleaned, FileInfo output, float scale = 1) {
        this.vits ??= Py.Import("craft_vits");
        this.vits.pth(config.FullName, model.FullName, cleaned, output.FullName, scale);
    }

    public void Dispose() {
        this.gil.Dispose();
        PythonEngine.Shutdown();
    }
}
