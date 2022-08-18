using Python.Runtime;

Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", "python38.dll");
PythonEngine.PythonHome = "C:\\Users\\SoarT\\scoop\\apps\\python38\\current";
PythonEngine.Initialize();

using (Py.GIL()) {
    dynamic sys = Py.Import("sys");
    sys.path.append("E:\\Codes\\Vits\\Runtime\\CleanerTest");

    dynamic clr = Py.Import("cleaner");
    dynamic res = clr.japanese_cleaner("どうしてこうなるんだろう。");

    Console.WriteLine(res);
}
