using UnityEngine;
using TMPro;
using System.Collections;

/// <summary>
/// Displays dialogue text in both a speech bubble and subtitles then fades them out.
/// </summary>
public class SpeechUI : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI bubbleText;
    [SerializeField] private TextMeshProUGUI subtitleText;
    [SerializeField] private float fadeDuration = 1f;
    [SerializeField] private float holdDuration = 2f;

    private Coroutine routine;

    /// <summary>
    /// Show text coming from the Python backend.
    /// </summary>
    public void Show(string text)
    {
        if (routine != null)
            StopCoroutine(routine);
        routine = StartCoroutine(Display(text));
    }

    private IEnumerator Display(string text)
    {
        if (bubbleText != null) bubbleText.text = text;
        if (subtitleText != null) subtitleText.text = text;
        SetAlpha(1f);
        yield return new WaitForSeconds(holdDuration);
        float t = 0f;
        while (t < fadeDuration)
        {
            t += Time.deltaTime;
            float a = Mathf.Lerp(1f, 0f, t / fadeDuration);
            SetAlpha(a);
            yield return null;
        }
        if (bubbleText != null) bubbleText.text = string.Empty;
        if (subtitleText != null) subtitleText.text = string.Empty;
        routine = null;
    }

    private void SetAlpha(float a)
    {
        if (bubbleText != null)
        {
            var c = bubbleText.color;
            c.a = a;
            bubbleText.color = c;
        }
        if (subtitleText != null)
        {
            var c = subtitleText.color;
            c.a = a;
            subtitleText.color = c;
        }
    }
}
