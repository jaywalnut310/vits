namespace VitsCLI;

using System;
using System.Diagnostics;
using System.IO.Compression;
using System.Linq;
using System.Net.Http.Handlers;
using System.Runtime.InteropServices;
using Python.Runtime;
using ShellProgressBar;

public static partial class Env {
    public static string OutName(string name) => $"{Path.GetFileNameWithoutExtension(name)}-{Random.Shared.Next()}.wav";

    public static async Task<bool> TryLoad(string[] args) {
        var p = Process.Start(Environment.ProcessPath!, args.Append("-t"));
        await p.WaitForExitAsync();
        return p.ExitCode == 0;
    }

    public static void AutoSetup(bool overwrite = false) {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            var path = Path.Combine(AppContext.BaseDirectory, "python38");
            var lib = Path.Combine(path, "Lib");

            if (overwrite || !File.Exists(Path.Combine(path, "python38.dll"))) {
                using var main = new ProgressBar(1, "安装运行时");

                Task.WaitAll(Task.Run(async () => {

                    using var bar = main.Spawn(100, "Download Python3.8");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var py =
                        await client.GetStreamAsync(
                            "https://mirrors.huaweicloud.com/python/3.8.10/python-3.8.10-embed-amd64.zip");
                    using var pyz = new ZipArchive(py);

                    bar.Message = "Extract Python3.8";
                    pyz.ExtractToDirectory(path, true);
                    bar.Message = "Python3.8 Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(100, "Download Numpy");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var np = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/fa/ca/5e0d36d65772b5ff586e94103cd9b2de216e544444651fc2681165c6d02c/numpy-1.23.2-cp38-cp38-win_amd64.whl");
                    using var npz = new ZipArchive(np);

                    bar.Message = "Extract Numpy";
                    npz.ExtractToDirectory(lib, true);
                    bar.Message = "Numpy Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(100, "Download PyTorch");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var tor = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/e7/ae/2e4166eae0a2693ad9233da1c927f5f1b4d050d9d906ba656e1771d7c852/torch-1.12.1-cp38-cp38-win_amd64.whl");
                    using var trz = new ZipArchive(tor);

                    bar.Message = "Extract PyTorch";
                    trz.ExtractToDirectory(lib, true);
                    bar.Message = "PyTorch Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(10, "Download tqdm");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var tqd = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/8a/c4/d15f1e627fff25443ded77ea70a7b5532d6371498f9285d44d62587e209c/tqdm-4.64.0-py2.py3-none-any.whl");
                    using var tqz = new ZipArchive(tqd);

                    bar.Message = "Extract tqdm";
                    tqz.ExtractToDirectory(lib, true);
                    bar.Message = "tqdm Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(10, "Download Unidecode");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var uni = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/f9/5b/7603add7f192252916b85927263b598c74585f82389e6e42318a6278159b/Unidecode-1.3.4-py3-none-any.whl");
                    using var unz = new ZipArchive(uni);

                    bar.Message = "Extract Unidecode";
                    unz.ExtractToDirectory(lib, true);
                    bar.Message = "Unidecode Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(10, "Download six");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var six = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/d9/5a/e7c31adbe875f2abbb91bd84cf2dc52d792b5a01506781dbcf25c91daf11/six-1.16.0-py2.py3-none-any.whl");
                    using var sxz = new ZipArchive(six);

                    bar.Message = "Extract six";
                    sxz.ExtractToDirectory(lib, true);
                    bar.Message = "six Installed";

                }), Task.Run(async () => {

                    using var bar = main.Spawn(10, "Download typing_extensions");
                    var pro = bar.AsProgress<int>();

                    using var handler = new ProgressMessageHandler(new HttpClientHandler());
                    handler.HttpReceiveProgress += (_, e) => pro.Report(e.ProgressPercentage);
                    using var client = new HttpClient(handler);

                    await using var typ = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/ed/d6/2afc375a8d55b8be879d6b4986d4f69f01115e795e36827fd3a40166028b/typing_extensions-4.3.0-py3-none-any.whl");
                    using var tpz = new ZipArchive(typ);

                    bar.Message = "Extract typing_extensions";
                    tpz.ExtractToDirectory(lib, true);
                    bar.Message = "typing_extensions Installed";

                }), Task.Run(() => {

                    using var bar = main.Spawn(1, "Install pyopenjtalk");
                    ZipFile.ExtractToDirectory(Path.Combine(AppContext.BaseDirectory, "pyopenjtalk.zip"), lib, true);
                    bar.AsProgress<int>().Report(1);
                }));
            }

            _ = SetPyDLL();
            SetPyLoc(path);

            PythonEngine.PythonPath = string.Join(";", path, lib,
                Path.Combine(path, "python38.zip"),
                Path.Combine(AppContext.BaseDirectory, "infer.zip"));
        } else
            throw new NotSupportedException("目前还不支持 Windows 以外的自动环境配置");
    }
}
