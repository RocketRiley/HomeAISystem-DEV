using System;
using System.Collections;
using System.Net.WebSockets;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

/// <summary>
/// Captures microphone audio and streams it to a Python STT service via WebSocket.
/// </summary>
public class SttCapture : MonoBehaviour
{
    /// <summary>
    /// Endpoint of the Python STT WebSocket server.
    /// </summary>
    public string sttEndpoint = "ws://localhost:5005/stt";

    /// <summary>
    /// Audio sampling rate in Hz.
    /// </summary>
    public int sampleRate = 16000;

    /// <summary>
    /// Size of audio chunks sent to the server in milliseconds.
    /// </summary>
    public int chunkMilliseconds = 250;

    private ClientWebSocket socket;
    private AudioClip micClip;
    private int lastSample;

    private async void Start()
    {
        socket = new ClientWebSocket();
        await socket.ConnectAsync(new Uri(sttEndpoint), CancellationToken.None);

        micClip = Microphone.Start(null, true, 1, sampleRate);
        lastSample = 0;
        StartCoroutine(StreamAudio());
    }

    private IEnumerator StreamAudio()
    {
        int chunkSize = sampleRate * chunkMilliseconds / 1000;
        float[] floatBuffer = new float[chunkSize];
        byte[] byteBuffer = new byte[chunkSize * 2]; // 16-bit PCM

        while (true)
        {
            int pos = Microphone.GetPosition(null);
            int diff = pos - lastSample;
            if (diff < 0) diff += micClip.samples;

            if (diff >= chunkSize)
            {
                micClip.GetData(floatBuffer, lastSample);
                ConvertFloatsToBytes(floatBuffer, byteBuffer);
                var sendTask = socket.SendAsync(new ArraySegment<byte>(byteBuffer), WebSocketMessageType.Binary, true, CancellationToken.None);
                while (!sendTask.IsCompleted) yield return null;
                lastSample = (lastSample + chunkSize) % micClip.samples;
            }
            yield return null;
        }
    }

    private static void ConvertFloatsToBytes(float[] samples, byte[] bytes)
    {
        for (int i = 0; i < samples.Length; i++)
        {
            short value = (short)(Mathf.Clamp(samples[i], -1f, 1f) * short.MaxValue);
            bytes[2 * i] = (byte)(value & 0xff);
            bytes[2 * i + 1] = (byte)((value >> 8) & 0xff);
        }
    }

    private async void OnDestroy()
    {
        if (socket != null)
        {
            await socket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
            socket.Dispose();
        }
        if (Microphone.IsRecording(null))
            Microphone.End(null);
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void AutoStart()
    {
        var go = new GameObject("SttCapture");
        DontDestroyOnLoad(go);
        go.AddComponent<SttCapture>();
    }
}
