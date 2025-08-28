using System.Collections;
using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// High-level brain that picks points of interest and triggers animation
/// states when the avatar reaches them.
/// </summary>
[RequireComponent(typeof(NavMeshAgent))]
[RequireComponent(typeof(Animator))]
public class CharacterAI_Director : MonoBehaviour
{
    public POIManager poiManager;
    public float decisionInterval = 8f;
    public float arriveDistance = 0.2f;

    NavMeshAgent agent;
    Animator animator;
    POIMarker currentTarget;

    void Awake()
    {
        agent = GetComponent<NavMeshAgent>();
        animator = GetComponent<Animator>();
    }

    void Start()
    {
        if (poiManager == null)
        {
            poiManager = FindObjectOfType<POIManager>();
        }
        StartCoroutine(DecisionLoop());
    }

    IEnumerator DecisionLoop()
    {
        while (true)
        {
            yield return new WaitForSeconds(decisionInterval);
            if (currentTarget != null || poiManager == null) continue;
            currentTarget = poiManager.GetRandom();
            if (currentTarget != null)
            {
                agent.SetDestination(currentTarget.transform.position);
                animator.SetBool("Walking", true);
            }
        }
    }

    void Update()
    {
        if (currentTarget == null) return;
        if (!agent.pathPending && agent.remainingDistance <= arriveDistance)
        {
            animator.SetBool("Walking", false);
            HandleArrival(currentTarget);
            currentTarget = null;
        }
    }

    void HandleArrival(POIMarker poi)
    {
        switch (poi.type)
        {
            case "Seat":
                animator.SetTrigger("SitDown");
                break;
            case "Desk":
                animator.SetTrigger("UseComputer");
                break;
            default:
                break;
        }
    }
}
