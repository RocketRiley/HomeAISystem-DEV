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
        // Listen on port 9000 which matches scripts/osc_bridge_stub.py
        server = new OscServer(9000);
        var disp = server.MessageDispatcher;
        disp.AddCallback("/avatar/parameters/Joy", OnJoy);
        disp.AddCallback("/avatar/parameters/Angry", OnAngry);
        disp.AddCallback("/avatar/parameters/Sorrow", OnSorrow);
        disp.AddCallback("/avatar/parameters/Fun", OnFun);
    }

    void OnJoy(string address, OscDataHandle data)
    {
        animator?.SetFloat("Joy", data.GetElementAsFloat(0));
    }

    void OnAngry(string address, OscDataHandle data)
    {
        animator?.SetFloat("Angry", data.GetElementAsFloat(0));
    }

    void OnSorrow(string address, OscDataHandle data)
    {
        animator?.SetFloat("Sorrow", data.GetElementAsFloat(0));
    }

    void OnFun(string address, OscDataHandle data)
    {
        animator?.SetFloat("Fun", data.GetElementAsFloat(0));
    }

    void OnDestroy()
    {
        server?.Dispose();
    }
}
