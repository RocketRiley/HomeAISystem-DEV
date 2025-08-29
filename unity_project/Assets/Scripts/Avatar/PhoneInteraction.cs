using System.Collections;
using UnityEngine;

/// <summary>
/// Handles spawning and cleanup of a phone prop for the avatar.
/// </summary>
public class PhoneInteraction : MonoBehaviour
{
    public GameObject phonePrefab;
    public Transform rightHand;
    public Animator animator;
    [Tooltip("Animator trigger to start phone usage.")]
    public string phoneTrigger = "UsePhone";
    [Tooltip("Animator state name representing phone usage.")]
    public string phoneStateName = "UsePhone";

    GameObject phoneInstance;

    /// <summary>
    /// Spawn the phone, attach it to the hand and start the animation.
    /// </summary>
    public void StartPhoneUse()
    {
        if (phoneInstance != null) return;
        if (phonePrefab == null || rightHand == null || animator == null) return;

        phoneInstance = Instantiate(phonePrefab, rightHand);
        phoneInstance.transform.localPosition = Vector3.zero;
        phoneInstance.transform.localRotation = Quaternion.identity;

        animator.SetTrigger(phoneTrigger);
        StartCoroutine(MonitorPhoneState());
    }

    IEnumerator MonitorPhoneState()
    {
        // Wait for the state to start.
        while (!animator.GetCurrentAnimatorStateInfo(0).IsName(phoneStateName))
            yield return null;
        // Wait for the state to finish.
        while (animator.GetCurrentAnimatorStateInfo(0).IsName(phoneStateName))
            yield return null;
        EndPhoneUse();
    }

    void EndPhoneUse()
    {
        if (phoneInstance != null)
        {
            Destroy(phoneInstance);
            phoneInstance = null;
        }
    }

    void OnDisable()
    {
        EndPhoneUse();
    }
}

