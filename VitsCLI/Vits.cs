namespace VitsCLI;

using System.Globalization;
using Python.Runtime;

public class Vits : IDisposable {
    private readonly Py.GILState gil;
    private dynamic? clr;
    private dynamic? vits;

    public Vits(string[] args, bool check = true) {
        if (check && !Env.TryLoad(args).Result)
            throw new("不能启动 Python，这可能是因为在 Local 模式时 PyDLL / PyLoc 设置错误；或自动安装的 Python 环境损坏导致的，可使用 --Reset 恢复");

        PythonEngine.Initialize();
        this.gil = Py.GIL();

        dynamic sys = Py.Import("sys");
        sys.path.append(AppContext.BaseDirectory + "infer.zip");
    }

    public string Clean(string str) {
        this.clr ??= Py.Import("cleaner");

        var res = this.clr.japanese_cleaner(str);
        Console.WriteLine("Cleaned: " + res);
        return res;
    }

    public void Do(string config, string model, string cleaned, string output, float scale = 1) {
        ArgumentException.ThrowIfNullOrEmpty(config);
        ArgumentException.ThrowIfNullOrEmpty(model);
        ArgumentException.ThrowIfNullOrEmpty(cleaned);
        ArgumentException.ThrowIfNullOrEmpty(output);

        this.vits ??= Py.Import("craft_vits");

        if (model.EndsWith(".pth", true, CultureInfo.InvariantCulture)) {
            this.vits.pth(config, model, cleaned, output, scale);
            return;
        }

        this.vits.pt(config, model, cleaned, output);
    }

    public void Dispose() {
        this.gil.Dispose();
        PythonEngine.Shutdown();
    }
}
