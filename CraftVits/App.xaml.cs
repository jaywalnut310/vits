// To learn more about WinUI, the WinUI project structure,
// and more about our project templates, see: http://aka.ms/winui-project-info.

namespace CraftVits;
using Microsoft.UI.Xaml;
using WinUIEx;

/// <summary>
/// Provides application-specific behavior to supplement the default Application class.
/// </summary>
public partial class App {
    private Window window;
    private WindowManager mgr;

    /// <summary>
    /// Initializes the singleton application object.  This is the first line of authored code
    /// executed, and as such is the logical equivalent of main() or WinMain().
    /// </summary>
    public App() => InitializeComponent();

    /// <summary>
    /// Invoked when the application is launched normally by the end user.  Other entry points
    /// will be used such as when the application is launched to open a specific file.
    /// </summary>
    /// <param name="args"> Details about the launch request and process. </param>
    protected override void OnLaunched(LaunchActivatedEventArgs args) {
        window = new MainWindow();
        mgr = WindowManager.Get(window);
        mgr.Backdrop = new AcrylicSystemBackdrop();

        window.Activate();
    }
}
