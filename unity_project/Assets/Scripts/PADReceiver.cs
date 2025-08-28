using UnityEngine;

/// <summary>
/// Maps emotion values received from the WebSocketClient to Animator parameters.
/// </summary>
public class PADReceiver : MonoBehaviour
{
    public Animator animator;
    public WebSocketClient client;

    void Start()
    {
        if (client == null)
            client = FindObjectOfType<WebSocketClient>();
        if (client != null)
            client.EmotionReceived += OnEmotion;
    }

    void OnDestroy()
    {
        if (client != null)
            client.EmotionReceived -= OnEmotion;
    }

    void OnEmotion(WebSocketClient.EmotionMessage msg)
    {
        animator?.SetFloat("Joy", msg.Joy);
        animator?.SetFloat("Angry", msg.Angry);
        animator?.SetFloat("Sorrow", msg.Sorrow);
        animator?.SetFloat("Fun", msg.Fun);
    }
}
