using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// Basic wandering behaviour inside a rectangular area.
/// Requires a NavMeshAgent and a baked NavMesh in the scene.
/// </summary>
public class RoamController : MonoBehaviour
{
    public bool enableRoam = false;
    public Vector3 areaCenter = Vector3.zero;
    public Vector3 areaSize = new Vector3(4f, 0f, 4f);
    public float waitTime = 5f;

    NavMeshAgent agent;
    float timer;

    void Awake()
    {
        agent = GetComponent<NavMeshAgent>();
        timer = waitTime;
    }

    void Update()
    {
        if (!enableRoam || agent == null) return;
        timer += Time.deltaTime;
        if (timer < waitTime) return;
        if (!agent.pathPending && agent.remainingDistance < 0.2f)
        {
            var half = areaSize * 0.5f;
            var randomPoint = new Vector3(
                Random.Range(areaCenter.x - half.x, areaCenter.x + half.x),
                transform.position.y,
                Random.Range(areaCenter.z - half.z, areaCenter.z + half.z)
            );
            if (NavMesh.SamplePosition(randomPoint, out var hit, 1f, NavMesh.AllAreas))
            {
                agent.SetDestination(hit.position);
                timer = 0f;
            }
        }
    }
}
