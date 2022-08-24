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
        Console.WriteLine("\nCleaned: " + res);
        return res;
    }

    public void Do(Cfg cfg, string cleaned) {
        ArgumentException.ThrowIfNullOrEmpty(cfg.Config);
        ArgumentException.ThrowIfNullOrEmpty(cfg.Model);
        ArgumentException.ThrowIfNullOrEmpty(cfg.Output);
        ArgumentException.ThrowIfNullOrEmpty(cleaned);

        this.vits ??= Py.Import("craft_vits");

        if (cfg.Model.EndsWith(".pth", true, CultureInfo.InvariantCulture)) {
            this.vits.pth(cfg, cleaned);
            return;
        }

        this.vits.pt(cfg, cleaned);
    }

    public void Dispose() {
        this.gil.Dispose();
        PythonEngine.Shutdown();
    }
}
