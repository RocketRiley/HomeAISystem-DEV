using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using TMPro;

/// <summary>
/// Fetches configuration from <c>scripts/settings_server.py</c> and allows
/// switching STT/TTS engines and processing mode. Changes are posted back to
/// the server and interested subsystems can be reloaded via UnityEvents.
/// </summary>
public class SettingsMenu : MonoBehaviour
{
    [SerializeField] private TMP_Dropdown sttDropdown;
    [SerializeField] private TMP_Dropdown ttsDropdown;
    [SerializeField] private TMP_Dropdown processingDropdown;
    [SerializeField] private string serverUrl = "http://localhost:8765/config";

    public UnityEvent onSttChanged;
    public UnityEvent onTtsChanged;
    public UnityEvent onProcessingChanged;

    private void Start()
    {
        StartCoroutine(LoadConfig());
        sttDropdown.onValueChanged.AddListener(_ => OnSttChanged());
        ttsDropdown.onValueChanged.AddListener(_ => OnTtsChanged());
        processingDropdown.onValueChanged.AddListener(_ => OnProcessingChanged());
    }

    private IEnumerator LoadConfig()
    {
        using UnityWebRequest req = UnityWebRequest.Get(serverUrl);
        yield return req.SendWebRequest();
        if (req.result == UnityWebRequest.Result.Success)
        {
            var cfg = JsonUtility.FromJson<Config>(req.downloadHandler.text);
            Apply(cfg);
        }
        else
        {
            Debug.LogWarning($"Failed to load settings: {req.error}");
        }
    }

    private void Apply(Config cfg)
    {
        if (!string.IsNullOrEmpty(cfg.STT_ENGINE))
            SetDropdownValue(sttDropdown, cfg.STT_ENGINE);
        if (!string.IsNullOrEmpty(cfg.TTS_ENGINE))
            SetDropdownValue(ttsDropdown, cfg.TTS_ENGINE);
        if (!string.IsNullOrEmpty(cfg.PROCESSING_MODE))
            SetDropdownValue(processingDropdown, cfg.PROCESSING_MODE);
    }

    private void SetDropdownValue(TMP_Dropdown dropdown, string value)
    {
        int index = dropdown.options.FindIndex(o => o.text == value);
        if (index >= 0)
            dropdown.SetValueWithoutNotify(index);
    }

    private void OnSttChanged()
    {
        string value = sttDropdown.options[sttDropdown.value].text;
        StartCoroutine(UpdateConfig("STT_ENGINE", value, onSttChanged));
    }

    private void OnTtsChanged()
    {
        string value = ttsDropdown.options[ttsDropdown.value].text;
        StartCoroutine(UpdateConfig("TTS_ENGINE", value, onTtsChanged));
    }

    private void OnProcessingChanged()
    {
        string value = processingDropdown.options[processingDropdown.value].text;
        StartCoroutine(UpdateConfig("PROCESSING_MODE", value, onProcessingChanged));
    }

    private IEnumerator UpdateConfig(string key, string value, UnityEvent callback)
    {
        string json = $"{{\"{key}\":\"{value}\"}}";
        byte[] body = System.Text.Encoding.UTF8.GetBytes(json);
        using UnityWebRequest req = new UnityWebRequest(serverUrl, UnityWebRequest.kHttpVerbPOST);
        req.uploadHandler = new UploadHandlerRaw(body);
        req.downloadHandler = new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type", "application/json");
        yield return req.SendWebRequest();
        if (req.result == UnityWebRequest.Result.Success || req.responseCode == 204)
        {
            callback?.Invoke();
        }
        else
        {
            Debug.LogWarning($"Failed to update settings: {req.error}");
        }
    }

    [System.Serializable]
    private class Config
    {
        public string STT_ENGINE;
        public string TTS_ENGINE;
        public string PROCESSING_MODE;
    }
}
