using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// Basic wandering behaviour inside a rectangular area and simple interaction
/// with tagged targets.  The controller updates an <see cref="Animator"/> based
/// on the agent's movement speed and the type of target reached.
/// </summary>
public class RoamController : MonoBehaviour
{
    [Header("Roaming")]
    public bool enableRoam = false;
    public bool useRoamBounds = true;
    public Vector3 areaCenter = Vector3.zero;
    public Vector3 areaSize = new Vector3(4f, 0f, 4f);
    public float waitTime = 5f;

    [Header("Interaction Targets")]    
    public string[] targetTags = new [] { "Chair", "Bed", "Desk" };
    public float arrivalThreshold = 0.2f;

    [Header("Animation")]
    public Animator animator;

    NavMeshAgent agent;
    float timer;
    string currentTargetTag;

    void Awake()
    {
        agent = GetComponent<NavMeshAgent>();
        if (animator == null) animator = GetComponent<Animator>();
        timer = waitTime;
    }

    void Update()
    {
        if (!enableRoam || agent == null) return;

        timer += Time.deltaTime;

        // Update animator with movement speed
        if (animator != null)
        {
            animator.SetFloat("Speed", agent.velocity.magnitude);
        }

        if (timer < waitTime) return;

        if (!agent.pathPending && agent.remainingDistance < arrivalThreshold)
        {
            // Trigger animation when reaching a tagged target
            if (!string.IsNullOrEmpty(currentTargetTag))
            {
                TriggerAnimationForTag(currentTargetTag);
                currentTargetTag = null;
                timer = 0f;
                return;
            }

            Vector3 destination;
            if (TryGetTaggedDestination(out destination, out currentTargetTag))
            {
                agent.SetDestination(destination);
                timer = 0f;
            }
            else if (TryGetRandomRoamPoint(out destination))
            {
                agent.SetDestination(destination);
                timer = 0f;
            }
        }
    }

    /// <summary>
    /// Try to find a random destination on the navmesh.  If roaming bounds are
    /// enabled, the point is restricted to the configured area.
    /// </summary>
    bool TryGetRandomRoamPoint(out Vector3 position)
    {
        Vector3 randomPoint;
        if (useRoamBounds)
        {
            var half = areaSize * 0.5f;
            randomPoint = new Vector3(
                Random.Range(areaCenter.x - half.x, areaCenter.x + half.x),
                transform.position.y,
                Random.Range(areaCenter.z - half.z, areaCenter.z + half.z)
            );
        }
        else
        {
            randomPoint = transform.position + Random.insideUnitSphere * areaSize.magnitude;
            randomPoint.y = transform.position.y;
        }

        if (NavMesh.SamplePosition(randomPoint, out var hit, 1f, NavMesh.AllAreas))
        {
            position = hit.position;
            return true;
        }

        position = Vector3.zero;
        return false;
    }

    /// <summary>
    /// Select a random GameObject with one of the specified tags and return its
    /// position and tag.
    /// </summary>
    bool TryGetTaggedDestination(out Vector3 position, out string tag)
    {
        foreach (var t in targetTags)
        {
            var objs = GameObject.FindGameObjectsWithTag(t);
            if (objs != null && objs.Length > 0)
            {
                var dest = objs[Random.Range(0, objs.Length)].transform.position;
                position = dest;
                tag = t;
                return true;
            }
        }
        position = Vector3.zero;
        tag = null;
        return false;
    }

    void TriggerAnimationForTag(string tag)
    {
        if (animator == null) return;

        animator.SetInteger("TargetType", TagToId(tag));
        switch (tag)
        {
            case "Chair":
                animator.SetTrigger("Sit");
                break;
            case "Bed":
                animator.SetTrigger("Sleep");
                break;
            case "Desk":
                animator.SetTrigger("Work");
                break;
        }
    }

    int TagToId(string tag)
    {
        switch (tag)
        {
            case "Chair": return 1;
            case "Bed": return 2;
            case "Desk": return 3;
            default: return 0;
        }
    }
}
