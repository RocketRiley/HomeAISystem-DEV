using UnityEngine;
using System;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;
using System.Text;

/// <summary>
/// Runtime diagnostics overlay that shows connection status and last errors.
/// Connects to the Python log manager via WebSocket to receive log entries
/// and displays the most recent error message.  The overlay can be toggled
/// with the F3 key.
/// </summary>
public class DiagnosticsHUD : MonoBehaviour
{
    /// <summary>Key used to toggle the HUD visibility.</summary>
    public KeyCode toggleKey = KeyCode.F3;

    /// <summary>WebSocket endpoint served by scripts/log_manager.py.</summary>
    public string websocketUrl = "ws://localhost:8765";

    bool _visible = true;
    string _oscStatus = "Unknown";
    string _wsStatus = "Disconnected";
    string _sttEngine = string.Empty;
    string _ttsEngine = string.Empty;
    string _lastError = string.Empty;

    ClientWebSocket _ws;
    CancellationTokenSource _cts;

    void Start()
    {
        ConnectWebSocket();
    }

    async void ConnectWebSocket()
    {
        _ws = new ClientWebSocket();
        _cts = new CancellationTokenSource();
        try
        {
            await _ws.ConnectAsync(new Uri(websocketUrl), _cts.Token);
            _wsStatus = "Connected";
            _ = ReceiveLoop();
        }
        catch (Exception ex)
        {
            _wsStatus = "Error";
            _lastError = ex.Message;
        }
    }

    async Task ReceiveLoop()
    {
        var buffer = new byte[2048];
        while (_ws != null && _ws.State == WebSocketState.Open)
        {
            try
            {
                var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await _ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, _cts.Token);
                    _wsStatus = "Closed";
                }
                else
                {
                    var msg = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    ProcessLogMessage(msg);
                }
            }
            catch (Exception ex)
            {
                _wsStatus = "Error";
                _lastError = ex.Message;
                break;
            }
        }
    }

    void ProcessLogMessage(string msg)
    {
        try
        {
            var entry = JsonUtility.FromJson<LogEntry>(msg);
            if (!string.IsNullOrEmpty(entry.level) && entry.level.ToLower() == "error")
            {
                _lastError = entry.message;
            }
            if (!string.IsNullOrEmpty(entry.stt))
                _sttEngine = entry.stt;
            if (!string.IsNullOrEmpty(entry.tts))
                _ttsEngine = entry.tts;
        }
        catch
        {
            // Ignore malformed log messages
        }
    }

    void Update()
    {
        if (Input.GetKeyDown(toggleKey))
            _visible = !_visible;

        var receiver = FindObjectOfType<PADReceiver>();
        _oscStatus = receiver != null ? "Listening" : "Not Listening";
    }

    void OnGUI()
    {
        if (!_visible)
            return;

        GUILayout.BeginArea(new Rect(10, 10, 420, 140), GUI.skin.box);
        GUILayout.Label($"OSC: {_oscStatus}");
        GUILayout.Label($"WebSocket: {_wsStatus}");
        GUILayout.Label($"STT: {_sttEngine}");
        GUILayout.Label($"TTS: {_ttsEngine}");
        GUILayout.Label($"Last error: {_lastError}");
        GUILayout.EndArea();
    }

    void OnDestroy()
    {
        try
        {
            _cts?.Cancel();
            _ws?.Dispose();
        }
        catch { }
    }

    [Serializable]
    class LogEntry
    {
        public string level;
        public string message;
        public string stt;
        public string tts;
    }
}

