using UnityEngine;
using UnityEngine.UI;
using System.IO;

/// <summary>
/// Minimal settings menu allowing editing of the room configuration.
/// </summary>
public class SettingsMenu : MonoBehaviour
{
    public InputField roomPrefabInput;

    string ConfigPath => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "config", "room_config.json"));

    void Start()
    {
        Load();
    }

    /// <summary>
    /// Loads current configuration into the UI input field.
    /// </summary>
    public void Load()
    {
        if (roomPrefabInput == null) return;
        var config = ReadConfig();
        roomPrefabInput.text = config.roomPrefab;
    }

    /// <summary>
    /// Saves the configuration back to <c>room_config.json</c>.
    /// </summary>
    public void Save()
    {
        if (roomPrefabInput == null) return;
        var config = new RoomConfig { roomPrefab = roomPrefabInput.text };
        var json = JsonUtility.ToJson(config, true);
        File.WriteAllText(ConfigPath, json);
    }

    RoomConfig ReadConfig()
    {
        try
        {
            if (File.Exists(ConfigPath))
            {
                var json = File.ReadAllText(ConfigPath);
                return JsonUtility.FromJson<RoomConfig>(json);
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"SettingsMenu: Failed to read config - {e.Message}");
        }
        return new RoomConfig();
    }
}
