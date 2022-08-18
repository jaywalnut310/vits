namespace VitsCLI;

using Python.Runtime;

public class Vits {
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

    public void PT(FileInfo config, FileInfo model, string cleaned) {
        this.vits ??= Py.Import("craft_vits");

        var res = this.vits.pt_do(config.FullName, model.FullName, cleaned);
    }

    public void PTH(FileInfo config, FileInfo model, string cleaned, float scale = 1) {

    }

    ~Vits() {
        this.gil.Dispose();
        PythonEngine.Shutdown();
    }
}
