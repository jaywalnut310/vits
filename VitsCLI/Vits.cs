namespace VitsCLI;

using Python.Runtime;

public class Vits : IDisposable {
    private readonly Py.GILState gil;
    private readonly dynamic clr;

    public Vits() {
        PythonEngine.Initialize();
        this.gil = Py.GIL();

        dynamic sys = Py.Import("sys");
        sys.path.append(AppContext.BaseDirectory);

        this.clr = Py.Import("cleaner");
    }

    public string Clean(string str) {
        var res = this.clr.japanese_cleaner(str);
        Console.WriteLine(res);
        return res;
    }

    public void Dispose() {
        this.gil.Dispose();
        PythonEngine.Shutdown();
    }
}
