using UnityEngine;

/// <summary>
/// Adds subtle head micro-motions using Perlin noise so the avatar
/// appears lively even when idle.
/// </summary>
public class MicroMotion : MonoBehaviour
{
    public Transform target; // head transform
    public float amplitude = 1f; // degrees
    public float speed = 0.5f;   // oscillations per second
    Vector3 baseEuler;

    void Start()
    {
        if (target == null) target = transform;
        baseEuler = target.localEulerAngles;
    }

    void Update()
    {
        if (target == null) return;
        float t = Time.time * speed;
        float x = (Mathf.PerlinNoise(t, 0f) * 2f - 1f) * amplitude;
        float y = (Mathf.PerlinNoise(0f, t) * 2f - 1f) * amplitude;
        target.localEulerAngles = baseEuler + new Vector3(x, y, 0f);
    }
}
