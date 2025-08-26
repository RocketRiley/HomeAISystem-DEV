using UnityEngine;
using System.Diagnostics;
using System.IO;

/// <summary>
/// Launches the Python AI runtime when the Unity scene starts.
/// The Python executable can be overridden with the PYTHON_EXE
/// environment variable. The script path is assumed to be
/// ../../scripts/ui_launcher.py relative to the Unity project.
/// </summary>
public class PythonBridge : MonoBehaviour
{
    Process process;

    void Start()
    {
        string pythonExe = System.Environment.GetEnvironmentVariable("PYTHON_EXE");
        if (string.IsNullOrEmpty(pythonExe))
            pythonExe = "python";

        // Resolve the repo root two levels above Assets
        string repoRoot = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
        string scriptPath = Path.Combine(repoRoot, "scripts", "ui_launcher.py");

        var info = new ProcessStartInfo(pythonExe, scriptPath)
        {
            WorkingDirectory = repoRoot,
            UseShellExecute = false,
            CreateNoWindow = false
        };

        try
        {
            process = Process.Start(info);
        }
        catch (System.Exception e)
        {
            UnityEngine.Debug.LogError($"Failed to launch Python: {e.Message}");
        }
    }

    void OnApplicationQuit()
    {
        if (process != null && !process.HasExited)
        {
            process.Kill();
            process.Dispose();
        }
    }
}
