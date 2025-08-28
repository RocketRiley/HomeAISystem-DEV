using UnityEngine;
using System.IO;

/// <summary>
/// Serializable data structure for room configuration.
/// </summary>
[System.Serializable]
public class RoomConfig
{
    public string roomPrefab = "DefaultRoom";
}

/// <summary>
/// Loads a room prefab defined in <c>config/room_config.json</c> and
/// positions the avatar and camera at the prefab's spawn point.
/// </summary>
public class RoomLoader : MonoBehaviour
{
    public Transform avatar;
    public Vector3 cameraOffset = new Vector3(0f, 1.6f, -2f);

    void Start()
    {
        var config = LoadConfig();
        if (config == null || string.IsNullOrEmpty(config.roomPrefab)) return;

        var prefab = Resources.Load<GameObject>(config.roomPrefab);
        if (prefab == null)
        {
            Debug.LogWarning($"RoomLoader: Prefab '{config.roomPrefab}' not found in Resources.");
            return;
        }

        var room = Instantiate(prefab);
        var spawn = room.transform.Find("SpawnPoint");

        if (spawn != null)
        {
            if (avatar == null)
            {
                var obj = GameObject.FindWithTag("Player");
                avatar = obj != null ? obj.transform : null;
            }

            if (avatar != null)
            {
                avatar.position = spawn.position;
            }

            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.position = spawn.position + cameraOffset;
                if (avatar != null)
                {
                    cam.transform.LookAt(avatar);
                }
            }
        }
    }

    RoomConfig LoadConfig()
    {
        try
        {
            var path = Path.Combine(Application.dataPath, "..", "..", "config", "room_config.json");
            path = Path.GetFullPath(path);
            if (!File.Exists(path))
            {
                return new RoomConfig();
            }
            var json = File.ReadAllText(path);
            return JsonUtility.FromJson<RoomConfig>(json);
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"RoomLoader: Failed to load config - {e.Message}");
            return new RoomConfig();
        }
    }
}
