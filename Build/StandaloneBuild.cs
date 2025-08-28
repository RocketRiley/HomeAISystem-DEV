using System.IO;
using UnityEditor;
using UnityEngine;

public static class StandaloneBuild
{
    [MenuItem("Build/Standalone")]
    public static void BuildProject()
    {
        // Root build directory
        string buildDir = Path.Combine(Application.dataPath, "..", "Build");
        string dataDir = Path.Combine(buildDir, "Data");
        Directory.CreateDirectory(dataDir);

        // Build player
        string[] scenes = { "Assets/Scenes/Main.unity" };
        var options = new BuildPlayerOptions
        {
            scenes = scenes,
            locationPathName = Path.Combine(buildDir, "Clair.exe"),
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };
        BuildPipeline.BuildPlayer(options);

        // Copy Python scripts
        string scriptsSrc = Path.Combine(Application.dataPath, "..", "scripts");
        string scriptsDst = Path.Combine(dataDir, "scripts");
        CopyDirectory(scriptsSrc, scriptsDst);

        // Copy model assets
        string assetsSrc = Path.Combine(Application.dataPath, "..", "assets");
        string assetsDst = Path.Combine(dataDir, "assets");
        CopyDirectory(assetsSrc, assetsDst);

        // Generate wrapper scripts
        CreateWrappers(buildDir);
    }

    static void CopyDirectory(string sourceDir, string destinationDir)
    {
        if (!Directory.Exists(sourceDir))
        {
            Debug.LogWarning($"Source directory not found: {sourceDir}");
            return;
        }

        foreach (string dir in Directory.GetDirectories(sourceDir, "*", SearchOption.AllDirectories))
        {
            Directory.CreateDirectory(dir.Replace(sourceDir, destinationDir));
        }

        foreach (string file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
        {
            string dest = file.Replace(sourceDir, destinationDir);
            Directory.CreateDirectory(Path.GetDirectoryName(dest)!);
            File.Copy(file, dest, true);
        }
    }

    static void CreateWrappers(string buildDir)
    {
        string exeName = "Clair.exe";
        string pythonScript = "Data/scripts/chat_gui.py";

        string bat = $"@echo off\nstart \"Unity\" \"%~dp0{exeName}\"\npython %~dp0{pythonScript}\n";
        File.WriteAllText(Path.Combine(buildDir, "run.bat"), bat);

        string sh = $"#!/bin/sh\n\"$(dirname \"$0\")/{exeName}\" &\npython \"$(dirname \"$0\")/{pythonScript}\"\n";
        string shPath = Path.Combine(buildDir, "run.sh");
        File.WriteAllText(shPath, sh);

#if !UNITY_EDITOR_WIN
        try
        {
            var process = new System.Diagnostics.Process();
            process.StartInfo.FileName = "chmod";
            process.StartInfo.Arguments = $"+x \"{shPath}\"";
            process.StartInfo.CreateNoWindow = true;
            process.StartInfo.UseShellExecute = false;
            process.Start();
            process.WaitForExit();
        }
        catch { }
#endif
    }
}
