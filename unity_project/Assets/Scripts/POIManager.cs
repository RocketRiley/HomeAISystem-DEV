using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Scans the scene for objects tagged as Interactable and caches their
/// <see cref="POIMarker"/> components. Other systems query this to pick
/// destinations for the avatar.
/// </summary>
public class POIManager : MonoBehaviour
{
    public List<POIMarker> points = new List<POIMarker>();

    void Awake()
    {
        points.Clear();
        var objs = GameObject.FindGameObjectsWithTag("Interactable");
        foreach (var obj in objs)
        {
            var marker = obj.GetComponent<POIMarker>();
            if (marker != null)
            {
                points.Add(marker);
            }
        }
    }

    /// <summary>
    /// Returns a random point of interest. Optionally filter by subtype.
    /// </summary>
    public POIMarker GetRandom(string subtype = null)
    {
        List<POIMarker> list;
        if (string.IsNullOrEmpty(subtype))
        {
            list = points;
        }
        else
        {
            list = points.FindAll(p => p.type == subtype);
        }
        if (list.Count == 0) return null;
        return list[Random.Range(0, list.Count)];
    }
}
