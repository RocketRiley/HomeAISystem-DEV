using UnityEngine;

/// <summary>
/// Simple surface-aligned grounding for the avatar. Adjusts feet and pelvis
/// using Animator IK so that the character correctly aligns with arbitrary
/// floor heights and slopes.
/// </summary>
[RequireComponent(typeof(Animator))]
public class IKGrounding : MonoBehaviour
{
    public LayerMask groundMask = ~0;
    public float rayLength = 1.5f;
    public float pelvisOffset = 0f;

    Animator animator;

    void Awake()
    {
        animator = GetComponent<Animator>();
    }

    void OnAnimatorIK(int layerIndex)
    {
        AdjustFoot(AvatarIKGoal.LeftFoot);
        AdjustFoot(AvatarIKGoal.RightFoot);
        AlignPelvis();
    }

    void AdjustFoot(AvatarIKGoal foot)
    {
        var footPos = animator.GetIKPosition(foot);
        if (Physics.Raycast(footPos + Vector3.up, Vector3.down, out var hit, rayLength, groundMask))
        {
            animator.SetIKPositionWeight(foot, 1f);
            animator.SetIKRotationWeight(foot, 1f);
            animator.SetIKPosition(foot, hit.point);
            animator.SetIKRotation(foot, Quaternion.LookRotation(transform.forward, hit.normal));
        }
        else
        {
            animator.SetIKPositionWeight(foot, 0f);
            animator.SetIKRotationWeight(foot, 0f);
        }
    }

    void AlignPelvis()
    {
        if (Physics.Raycast(transform.position + Vector3.up, Vector3.down, out var hit, rayLength, groundMask))
        {
            var pos = transform.position;
            pos.y = hit.point.y + pelvisOffset;
            transform.position = pos;
        }
    }
}
