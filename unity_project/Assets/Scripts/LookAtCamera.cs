using UnityEngine;

/// <summary>
/// Simple component that rotates the avatar to face the main camera.
/// Toggle <see cref="enableLookAt"/> to enable or disable behaviour.
/// </summary>
public class LookAtCamera : MonoBehaviour
{
    public bool enableLookAt = true;

    void Update()
    {
        if (!enableLookAt) return;
        var cam = Camera.main;
        if (cam == null) return;
        var target = cam.transform.position;
        target.y = transform.position.y; // keep upright
        transform.LookAt(target);
    }
}
