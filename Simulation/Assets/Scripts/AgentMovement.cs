using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AgentMovement : MonoBehaviour
{
    // Inputs:
    public GameObject foodPrefab;
    public float speed = 5f;
    public CharacterController controller;
    public LayerMask groundLayer;
    public int food = 0;

    // Fields:
    float velY = 0f;

    // Constants:
    const float GRAVITY = -9.81f * 4;

    /*
     * Moving the agent
     * Input : angle - the turning angle
     * Output: < None >
     */
    public void move(float angle)
    {
        // Movement:
        Quaternion rot = new Quaternion();
        rot.eulerAngles = new Vector3(0, transform.rotation.eulerAngles.y + angle, 0);
        transform.rotation = rot;
        controller.Move(transform.forward * speed * Time.deltaTime);

        // Gravity:
        velY += GRAVITY * Time.deltaTime;
        controller.Move(new Vector3(0, velY * Time.deltaTime, 0));
    }

    /*
     * Drawing gizmos
     * Input : < None >
     * Output: < None >
     */
    void OnDrawGizmos()
    {
        Gizmos.color = Color.green;
        Gizmos.DrawLine(transform.position, transform.position + transform.forward * 5);
        Gizmos.color = Color.blue;
        Gizmos.DrawRay(transform.position, Quaternion.AngleAxis(30, transform.up) * transform.forward);
        Gizmos.DrawRay(transform.position, Quaternion.AngleAxis(-30, transform.up) * transform.forward);
    }
}
