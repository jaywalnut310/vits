namespace VitsCLI;

using System.Diagnostics;
using System.IO.Compression;
using System.Linq;
using System.Runtime.InteropServices;
using Python.Runtime;

public static partial class Env {
    public static string OutName(string name) => $"{Path.GetFileNameWithoutExtension(name)}-{Random.Shared.Next()}.wav";

    public static async Task<bool> TryLoad(string[] args) {
        var p = Process.Start(Environment.ProcessPath!, args.Append("-t"));
        await p.WaitForExitAsync();
        return p.ExitCode == 0;
    }

    public static async Task AutoSetup(bool overwrite = false) {
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows)) {
            var path = Path.Combine(AppContext.BaseDirectory, "python38");
            var lib = Path.Combine(path, "Lib");

            if (overwrite || !File.Exists(Path.Combine(path, "python38.dll"))) {
                using var client = new HttpClient();

                {
                    Console.WriteLine("安装 python3.8");
                    await using var py = await client.GetStreamAsync("https://mirrors.huaweicloud.com/python/3.8.10/python-3.8.10-embed-amd64.zip");
                    using var pyz = new ZipArchive(py);
                    pyz.ExtractToDirectory(path, true);
                }

                {
                    Console.WriteLine("安装 numpy");
                    await using var np = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/fa/ca/5e0d36d65772b5ff586e94103cd9b2de216e544444651fc2681165c6d02c/numpy-1.23.2-cp38-cp38-win_amd64.whl");
                    using var npz = new ZipArchive(np);
                    npz.ExtractToDirectory(lib, true);
                }

                {
                    Console.WriteLine("安装 torch");
                    await using var tor = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/e7/ae/2e4166eae0a2693ad9233da1c927f5f1b4d050d9d906ba656e1771d7c852/torch-1.12.1-cp38-cp38-win_amd64.whl");
                    using var trz = new ZipArchive(tor);
                    trz.ExtractToDirectory(lib, true);
                }

                {
                    Console.WriteLine("安装 tqdm");
                    await using var tqd = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/8a/c4/d15f1e627fff25443ded77ea70a7b5532d6371498f9285d44d62587e209c/tqdm-4.64.0-py2.py3-none-any.whl");
                    using var tqz = new ZipArchive(tqd);
                    tqz.ExtractToDirectory(lib, true);
                }

                {
                    Console.WriteLine("安装 unidecode");
                    await using var uni = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/f9/5b/7603add7f192252916b85927263b598c74585f82389e6e42318a6278159b/Unidecode-1.3.4-py3-none-any.whl");
                    using var unz = new ZipArchive(uni);
                    unz.ExtractToDirectory(lib, true);
                }

                {
                    Console.WriteLine("安装 six");
                    await using var six = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/d9/5a/e7c31adbe875f2abbb91bd84cf2dc52d792b5a01506781dbcf25c91daf11/six-1.16.0-py2.py3-none-any.whl");
                    using var sxz = new ZipArchive(six);
                    sxz.ExtractToDirectory(lib, true);
                }

                {
                    Console.WriteLine("安装 typing_extensions");
                    await using var typ = await client.GetStreamAsync(
                        "https://pypi.tuna.tsinghua.edu.cn/packages/ed/d6/2afc375a8d55b8be879d6b4986d4f69f01115e795e36827fd3a40166028b/typing_extensions-4.3.0-py3-none-any.whl");
                    using var tpz = new ZipArchive(typ);
                    tpz.ExtractToDirectory(lib, true);
                }

                Console.WriteLine("安装 pyopenjtalk");
                ZipFile.ExtractToDirectory(Path.Combine(AppContext.BaseDirectory, "pyopenjtalk.zip"), lib, true);
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
