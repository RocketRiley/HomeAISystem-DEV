using UnityEngine;
using OscJack;

/// <summary>
/// Minimal OSC listener that maps PAD values from the Python app
/// to Animator parameters. Requires the OscJack package
/// (https://github.com/keijiro/OscJack).
/// </summary>
public class PADReceiver : MonoBehaviour
{
    public Animator animator;

    OscServer server;

    void Awake()
    {
        if (animator == null) animator = GetComponent<Animator>();
        // Listen on port 9000 which matches scripts/osc_bridge_stub.py
        server = new OscServer(9000);
        var disp = server.MessageDispatcher;
        disp.AddCallback("/avatar/parameters/Joy", OnJoy);
        disp.AddCallback("/avatar/parameters/Angry", OnAngry);
        disp.AddCallback("/avatar/parameters/Sorrow", OnSorrow);
        disp.AddCallback("/avatar/parameters/Fun", OnFun);
        disp.AddCallback("/avatar/parameters/MouthOpen", OnMouthOpen);
    }

    void OnJoy(string address, OscDataHandle data)
    {
        float v = Mathf.Clamp(data.GetElementAsFloat(0), -0.6f, 0.6f);
        animator?.SetFloat("Joy", v);
    }

    void OnAngry(string address, OscDataHandle data)
    {
        float v = Mathf.Clamp(data.GetElementAsFloat(0), -0.6f, 0.6f);
        animator?.SetFloat("Angry", v);
    }

    void OnSorrow(string address, OscDataHandle data)
    {
        float v = Mathf.Clamp(data.GetElementAsFloat(0), -0.6f, 0.6f);
        animator?.SetFloat("Sorrow", v);
    }

    void OnFun(string address, OscDataHandle data)
    {
        float v = Mathf.Clamp(data.GetElementAsFloat(0), -0.6f, 0.6f);
        animator?.SetFloat("Fun", v);
    }

    void OnMouthOpen(string address, OscDataHandle data)
    {
        float v = Mathf.Clamp(data.GetElementAsFloat(0), -0.6f, 0.6f);
        animator?.SetFloat("MouthOpen", v);
    }

    void OnMouthOpen(string address, OscDataHandle data)
    {
        animator?.SetFloat("MouthOpen", data.GetElementAsFloat(0));
    }

    void OnDestroy()
    {
        server?.Dispose();
    }
}
