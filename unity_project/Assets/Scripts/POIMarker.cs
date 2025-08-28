using UnityEngine;

/// <summary>
/// Attach to any object that should be considered a point of interest.
/// The <see cref="type"/> field describes what action the character can
/// perform at this location (e.g., "Seat", "Bed", "Desk").
/// </summary>
public class POIMarker : MonoBehaviour
{
    [Tooltip("Subtype used by the AI director, e.g., Seat, Bed, Desk, Teapot")]
    public string type = "Seat";
}
