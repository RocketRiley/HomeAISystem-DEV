using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Lightweight controller for in-world UI elements such as subtitles,
/// speech bubbles and runtime panels.
/// Other systems call into this to show or hide UI.
/// </summary>
public class UIManager : MonoBehaviour
{
    public Text subtitleText;
    public GameObject speechBubblePanel;
    public Text speechBubbleText;
    public GameObject settingsPanel;
    public GameObject diagnosticsPanel;

    public void ShowSubtitle(string text)
    {
        if (subtitleText != null) subtitleText.text = text;
    }

    public void ClearSubtitle()
    {
        if (subtitleText != null) subtitleText.text = string.Empty;
    }

    public void ShowSpeechBubble(string text)
    {
        if (speechBubblePanel != null) speechBubblePanel.SetActive(true);
        if (speechBubbleText != null) speechBubbleText.text = text;
    }

    public void HideSpeechBubble()
    {
        if (speechBubblePanel != null) speechBubblePanel.SetActive(false);
    }

    public void ToggleSettings(bool show)
    {
        if (settingsPanel != null) settingsPanel.SetActive(show);
    }

    public void ToggleDiagnostics(bool show)
    {
        if (diagnosticsPanel != null) diagnosticsPanel.SetActive(show);
    }
}
