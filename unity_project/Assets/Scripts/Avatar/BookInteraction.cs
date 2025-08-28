using System.Collections;
using UnityEngine;

/// <summary>
/// Handles spawning and cleanup of a book prop for the avatar.
/// </summary>
public class BookInteraction : MonoBehaviour
{
    public GameObject bookPrefab;
    public Transform leftHand;
    public Animator animator;
    [Tooltip("Animator trigger to start reading.")]
    public string readTrigger = "ReadBook";
    [Tooltip("Animator state name representing reading.")]
    public string readStateName = "ReadBook";

    GameObject bookInstance;

    /// <summary>
    /// Spawn the book, attach it to the hand and start the animation.
    /// </summary>
    public void StartReading()
    {
        if (bookInstance != null) return;
        if (bookPrefab == null || leftHand == null || animator == null) return;

        bookInstance = Instantiate(bookPrefab, leftHand);
        bookInstance.transform.localPosition = Vector3.zero;
        bookInstance.transform.localRotation = Quaternion.identity;

        animator.SetTrigger(readTrigger);
        StartCoroutine(MonitorReadingState());
    }

    IEnumerator MonitorReadingState()
    {
        // Wait for the state to start.
        while (!animator.GetCurrentAnimatorStateInfo(0).IsName(readStateName))
            yield return null;
        // Wait for the state to finish.
        while (animator.GetCurrentAnimatorStateInfo(0).IsName(readStateName))
            yield return null;
        EndReading();
    }

    void EndReading()
    {
        if (bookInstance != null)
        {
            Destroy(bookInstance);
            bookInstance = null;
        }
    }

    void OnDisable()
    {
        EndReading();
    }
}

