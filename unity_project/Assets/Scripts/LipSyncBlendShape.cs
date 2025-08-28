using UnityEngine;
using VRM;

/// <summary>
/// Maps the Animator parameter 'MouthOpen' to the VRM 'A' blendshape.
/// Attach this to the avatar root and assign the Animator and
/// VRMBlendShapeProxy references.
/// </summary>
public class LipSyncBlendShape : MonoBehaviour
{
    public Animator animator;
    public VRMBlendShapeProxy proxy;

    void Awake()
    {
        if (animator == null) animator = GetComponent<Animator>();
        if (proxy == null) proxy = GetComponent<VRMBlendShapeProxy>() ?? GetComponentInChildren<VRMBlendShapeProxy>();
    }

    void Update()
    {
        if (animator == null || proxy == null) return;
        float mouth = animator.GetFloat("MouthOpen");
        proxy.ImmediatelySetValue(BlendShapeKey.CreateFromPreset(BlendShapePreset.A), mouth);
    }
}
