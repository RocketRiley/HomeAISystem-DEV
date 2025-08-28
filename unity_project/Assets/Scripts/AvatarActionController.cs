using UnityEngine;
using OscJack;
using System;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;

/// <summary>
/// Listens for OSC and WebSocket events and updates Animator parameters
/// controlling avatar actions like talking, phone use, reading and roaming.
/// </summary>
public class AvatarActionController : MonoBehaviour
{
    public Animator animator;

    OscServer oscServer;
    ClientWebSocket ws;

    async void Awake()
    {
        // OSC setup
        oscServer = new OscServer(9001);
        var disp = oscServer.MessageDispatcher;
        disp.AddCallback("/avatar/action/talk", OnTalk);
        disp.AddCallback("/avatar/action/phone", OnPhone);
        disp.AddCallback("/avatar/action/read", OnRead);
        disp.AddCallback("/avatar/action/roam", OnRoam);

        // WebSocket setup
        ws = new ClientWebSocket();
        try
        {
            await ws.ConnectAsync(new Uri("ws://localhost:8080"), CancellationToken.None);
            _ = ReceiveLoop();
        }
        catch (Exception)
        {
            // ignore connection errors
        }
    }

    void OnTalk(string address, OscDataHandle data)
    {
        animator?.SetBool("isTalking", data.GetElementAsInt(0) != 0);
    }

    void OnPhone(string address, OscDataHandle data)
    {
        animator?.SetBool("usePhone", data.GetElementAsInt(0) != 0);
    }

    void OnRead(string address, OscDataHandle data)
    {
        animator?.SetBool("isReading", data.GetElementAsInt(0) != 0);
    }

    void OnRoam(string address, OscDataHandle data)
    {
        animator?.SetBool("isRoaming", data.GetElementAsInt(0) != 0);
    }

    async Task ReceiveLoop()
    {
        var buffer = new byte[1024];
        while (ws != null && ws.State == WebSocketState.Open)
        {
            var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            if (result.MessageType == WebSocketMessageType.Text)
            {
                var msg = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                HandleMessage(msg);
            }
        }
    }

    void HandleMessage(string msg)
    {
        switch (msg)
        {
            case "talk_on": animator?.SetBool("isTalking", true); break;
            case "talk_off": animator?.SetBool("isTalking", false); break;
            case "phone_on": animator?.SetBool("usePhone", true); break;
            case "phone_off": animator?.SetBool("usePhone", false); break;
            case "read_on": animator?.SetBool("isReading", true); break;
            case "read_off": animator?.SetBool("isReading", false); break;
            case "roam_on": animator?.SetBool("isRoaming", true); break;
            case "roam_off": animator?.SetBool("isRoaming", false); break;
        }
    }

    void OnDestroy()
    {
        oscServer?.Dispose();
        if (ws != null)
        {
            try
            {
                ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None).Wait(100);
            }
            catch {}
            ws.Dispose();
            ws = null;
        }
    }
}
