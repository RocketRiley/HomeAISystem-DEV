using UnityEngine;
using VRM;

/// <summary>
/// Applies Animator emotion parameters to VRM blendshapes.
/// Supports Joy, Angry, Sorrow and Fun.
/// </summary>
public class EmotionBlendShape : MonoBehaviour
{
    public Animator animator;
    public VRMBlendShapeProxy proxy;

    void Update()
    {
        if (animator == null || proxy == null) return;
        proxy.ImmediatelySetValue(BlendShapeKey.CreateFromPreset(BlendShapePreset.Joy), animator.GetFloat("Joy"));
        proxy.ImmediatelySetValue(BlendShapeKey.CreateFromPreset(BlendShapePreset.Angry), animator.GetFloat("Angry"));
        proxy.ImmediatelySetValue(BlendShapeKey.CreateFromPreset(BlendShapePreset.Sorrow), animator.GetFloat("Sorrow"));
        proxy.ImmediatelySetValue(BlendShapeKey.CreateFromPreset(BlendShapePreset.Fun), animator.GetFloat("Fun"));
    }
}
