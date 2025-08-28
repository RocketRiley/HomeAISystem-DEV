using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// Streams text to a Python TTS endpoint and plays the returned WAV audio.
/// Viseme timing data is exposed via <see cref="OnViseme"/> for lip-sync.
/// </summary>
public class TtsPlayer : MonoBehaviour
{
    [Serializable]
    public class Viseme
    {
        public string viseme; // Identifier from the TTS backend
        public float time;    // Time in seconds since start of audio
    }

    [Serializable]
    private class TtsResponse
    {
        public string audioUrl; // URL for WAV data
        public Viseme[] visemes; // Optional viseme timing data
    }

    /// <summary>
    /// Invoked when a viseme should be displayed. Arguments: viseme id, time in seconds.
    /// </summary>
    public event Action<string, float> OnViseme;

    /// <summary>
    /// Endpoint of the Python TTS service returning JSON with audioUrl and visemes.
    /// </summary>
    public string ttsEndpoint = "http://localhost:5005/tts";

    private AudioSource audioSource;

    private void Awake()
    {
        audioSource = gameObject.AddComponent<AudioSource>();
        audioSource.playOnAwake = false;
    }

    /// <summary>
    /// Request speech for the provided text.
    /// </summary>
    public void Speak(string text)
    {
        StartCoroutine(RequestTts(text));
    }

    private IEnumerator RequestTts(string text)
    {
        string url = ttsEndpoint + "?text=" + UnityWebRequest.EscapeURL(text);
        using (UnityWebRequest req = UnityWebRequest.Get(url))
        {
            yield return req.SendWebRequest();
            if (req.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("TTS request failed: " + req.error);
                yield break;
            }
            TtsResponse response = JsonUtility.FromJson<TtsResponse>(req.downloadHandler.text);
            yield return StartCoroutine(PlayResponse(response));
        }
    }

    private IEnumerator PlayResponse(TtsResponse response)
    {
        using (UnityWebRequest audioReq = UnityWebRequestMultimedia.GetAudioClip(response.audioUrl, AudioType.WAV))
        {
            yield return audioReq.SendWebRequest();
            if (audioReq.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Audio download failed: " + audioReq.error);
                yield break;
            }
            AudioClip clip = DownloadHandlerAudioClip.GetContent(audioReq);
            audioSource.clip = clip;
            audioSource.Play();
        }

        if (response.visemes != null && response.visemes.Length > 0)
        {
            StartCoroutine(EmitVisemes(response.visemes));
        }
    }

    private IEnumerator EmitVisemes(Viseme[] visemes)
    {
        float lastTime = 0f;
        foreach (var v in visemes)
        {
            float wait = Mathf.Max(0f, v.time - lastTime);
            lastTime = v.time;
            yield return new WaitForSeconds(wait);
            OnViseme?.Invoke(v.viseme, v.time);
        }
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void AutoStart()
    {
        var go = new GameObject("TtsPlayer");
        DontDestroyOnLoad(go);
        go.AddComponent<TtsPlayer>();
    }
}
