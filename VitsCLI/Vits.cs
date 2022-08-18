namespace VitsCLI;

using Python.Runtime;

public class Vits : IDisposable {
    private readonly dynamic clr;
    private dynamic? vits;

    public Vits() {
        PythonEngine.Initialize();

        using (Py.GIL()) {
            dynamic sys = Py.Import("sys");
            sys.path.append(AppContext.BaseDirectory);

            this.clr = Py.Import("cleaner");
            this.vits = Py.Import("craft_vits");
        }
    }

    public string Clean(string str) {
        using (Py.GIL()) {
            var res = this.clr.japanese_cleaner(str);
            Console.WriteLine(res);
            return res;
        }
    }

    public void PT(FileInfo config, FileInfo model, string cleaned) {
        PythonEngine.Initialize();

        using (Py.GIL()) {
            var res = this.vits.pt_do(config.FullName, model.FullName, cleaned);
        }
    }

    public void PTH(FileInfo config, FileInfo model, string cleaned, float scale = 1) {

    }

    public void Dispose() => PythonEngine.Shutdown();
}
