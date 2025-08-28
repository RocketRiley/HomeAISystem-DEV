using UnityEngine;
using UnityEngine.Animations.Rigging;

/// <summary>
/// Sets up two-bone IK constraints for arms and legs and allows toggling them.
/// Requires an Animator with a humanoid avatar and a RigBuilder component.
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(RigBuilder))]
public class IKRigController : MonoBehaviour
{
    public bool enableIK = true;

    [Header("Targets")]
    public Transform leftHandTarget;
    public Transform rightHandTarget;
    public Transform leftFootTarget;
    public Transform rightFootTarget;

    [Header("Hints")]
    public Transform leftArmHint;
    public Transform rightArmHint;
    public Transform leftLegHint;
    public Transform rightLegHint;

    RigBuilder rigBuilder;
    Rig armsRig;
    Rig legsRig;

    void Awake()
    {
        rigBuilder = GetComponent<RigBuilder>();
        BuildRig();
        SetIKActive(enableIK);
    }

    void BuildRig()
    {
        var animator = GetComponent<Animator>();

        armsRig = new GameObject("ArmsRig").AddComponent<Rig>();
        armsRig.transform.SetParent(transform);
        CreateLimbIK(armsRig.transform, animator,
            HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm, HumanBodyBones.LeftHand,
            leftHandTarget, leftArmHint, "LeftArmIK");
        CreateLimbIK(armsRig.transform, animator,
            HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand,
            rightHandTarget, rightArmHint, "RightArmIK");

        legsRig = new GameObject("LegsRig").AddComponent<Rig>();
        legsRig.transform.SetParent(transform);
        CreateLimbIK(legsRig.transform, animator,
            HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot,
            leftFootTarget, leftLegHint, "LeftLegIK");
        CreateLimbIK(legsRig.transform, animator,
            HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot,
            rightFootTarget, rightLegHint, "RightLegIK");

        rigBuilder.layers.Clear();
        rigBuilder.layers.Add(new RigLayer(armsRig));
        rigBuilder.layers.Add(new RigLayer(legsRig));
    }

    TwoBoneIKConstraint CreateLimbIK(Transform parent, Animator animator,
        HumanBodyBones rootBone, HumanBodyBones midBone, HumanBodyBones tipBone,
        Transform target, Transform hint, string name)
    {
        var go = new GameObject(name);
        go.transform.SetParent(parent);

        var ik = go.AddComponent<TwoBoneIKConstraint>();
        ik.data.root = animator.GetBoneTransform(rootBone);
        ik.data.mid = animator.GetBoneTransform(midBone);
        ik.data.tip = animator.GetBoneTransform(tipBone);
        ik.data.target = target;
        ik.data.hint = hint;
        return ik;
    }

    /// <summary>
    /// Enable or disable all IK rigs at runtime.
    /// </summary>
    public void SetIKActive(bool active)
    {
        enableIK = active;
        float weight = active ? 1f : 0f;
        if (armsRig != null) armsRig.weight = weight;
        if (legsRig != null) legsRig.weight = weight;
    }
}
