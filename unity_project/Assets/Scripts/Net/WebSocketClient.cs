using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// Simple WebSocket client that subscribes to emotion and transcript channels
/// from the Python backend and allows publishing UI events back to it.
/// </summary>
public class WebSocketClient : MonoBehaviour
{
    public string host = "ws://localhost:8765";

    ClientWebSocket emotionSocket;
    ClientWebSocket transcriptSocket;
    ClientWebSocket uiSocket;

    public event Action<EmotionMessage> EmotionReceived;
    public event Action<string> TranscriptReceived;

    [Serializable]
    public struct EmotionMessage
    {
        public float Joy;
        public float Angry;
        public float Sorrow;
        public float Fun;
    }

    async void Awake()
    {
        emotionSocket = await Connect("/emotion", HandleEmotion);
        transcriptSocket = await Connect("/transcript", HandleTranscript);
        uiSocket = await Connect("/ui", null);
    }

    async Task<ClientWebSocket> Connect(string path, Action<string> handler)
    {
        var ws = new ClientWebSocket();
        try
        {
            await ws.ConnectAsync(new Uri(host + path), CancellationToken.None);
            if (handler != null)
                _ = ReceiveLoop(ws, handler);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"WebSocket connect failed: {e.Message}");
        }
        return ws;
    }

    async Task ReceiveLoop(ClientWebSocket ws, Action<string> handler)
    {
        var buffer = new byte[1024];
        while (ws.State == WebSocketState.Open)
        {
            var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
            if (result.MessageType == WebSocketMessageType.Close)
                break;
            var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
            handler?.Invoke(msg);
        }
    }

    void HandleEmotion(string json)
    {
        try
        {
            var msg = JsonUtility.FromJson<EmotionMessage>(json);
            EmotionReceived?.Invoke(msg);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Emotion parse error: {e.Message}");
        }
    }

    void HandleTranscript(string json)
    {
        try
        {
            var wrapper = JsonUtility.FromJson<TranscriptWrapper>(json);
            TranscriptReceived?.Invoke(wrapper.text);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Transcript parse error: {e.Message}");
        }
    }

    [Serializable]
    class TranscriptWrapper { public string text; }

    public async void SendUIEvent(object payload)
    {
        if (uiSocket == null || uiSocket.State != WebSocketState.Open) return;
        var json = JsonUtility.ToJson(payload);
        var bytes = Encoding.UTF8.GetBytes(json);
        await uiSocket.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
    }

    async void OnDestroy()
    {
        if (emotionSocket != null)
            await emotionSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
        if (transcriptSocket != null)
            await transcriptSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
        if (uiSocket != null)
            await uiSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
    }
}
