using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

[System.Serializable]
public class InitSim
{
    // Fields:
    public int foodCount;
    public int agentCount;
    public List<string> foodKinds;
    public List<string> agentKinds;

    // Methods:
    public static InitSim CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<InitSim>(jsonString);
    }
}

[System.Serializable]
public class currStatus
{
    // Fields:
    public float[] foodList;
    public float[] agentList;

    // Methods:
    public string SaveToString()
    {
        return JsonUtility.ToJson(this);
    }
}

[System.Serializable]
public class angleChange
{
    // Fields:
    public List<float> angles;
    public List<int> eaten;
    public bool dead;

    // Methods:
    public static angleChange CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<angleChange>(jsonString);
    }
}

public class Communicator : MonoBehaviour
{
    // Inputs:
    public GameObject agentPrefab;
    public GameObject foodPrefab;
    public List<GameObject> foodList;
    public List<GameObject> agentList;

    // Constants:
    private NetworkStream socket;
    private const string IP = "127.0.0.1";
    private const int PORT = 2222;
    private const int SIZE = 2048;
    private const int DEAD_ANGLE_VALUE = 99999;

    /*
     * Sends a status message
     */
    void sendStatusMessage()
    {
        // Inits:
        currStatus status = new currStatus();

        // Getting the food list:
        status.foodList = new float[foodList.Count * 2];
        for (int i = 0; i < foodList.Count; i++)
        {
            status.foodList[i * 2] = foodList[i].transform.position.x;
            status.foodList[i * 2 + 1] = foodList[i].transform.position.z;
        }

        // Getting the agent list:
        status.agentList = new float[agentList.Count * 3];
        for (int i = 0; i < agentList.Count; i++)
        {
            status.agentList[i * 3] = agentList[i].transform.position.x;
            status.agentList[i * 3 + 1] = agentList[i].transform.position.z;
            status.agentList[i * 3 + 2] = -1 * (agentList[i].transform.eulerAngles.y - 90);
        }

        // Sending the status message:
        string statusJson = status.SaveToString();
        Write(statusJson);
    }


    /*
     * Spawning the environment
     * Input : initValues - the initialization values
     * Output: < None >
     */
    void SpawnEnv(InitSim initValues)
    {
        if (agentPrefab && foodPrefab)
        {
            // Removing all Food objects:
            for (int i = 0; i < foodList.Count; i++)
            {
                Destroy(foodList[i]);
            }
            foodList = null;
            foodList = new List<GameObject>();

            // Removing all Agent objects:
            for (int i = 0; i < agentList.Count; i++)
            {
                Destroy(agentList[i]);
            }
            agentList = null;
            agentList = new List<GameObject>();

            // Food spawning:
            for (int i = 0; i < initValues.foodCount; i++)
            {
                foodList.Add(Instantiate(foodPrefab, new Vector3(Random.Range(-5, 5), 0.8f, Random.Range(-5, 5)), Quaternion.identity));
            }

            // Agent spawning:
            for (int i = 0; i < initValues.agentCount; i++)
            {
                agentPrefab.GetComponent<MeshFilter>().mesh = SetMesh(initValues.agentKinds[i]);
                agentPrefab.GetComponent<MeshRenderer>().material = SetMaterial(initValues.agentKinds[i]);
                agentList.Add(Instantiate(agentPrefab, new Vector3(Random.Range(-5, 5), 0f, Random.Range(-5, 5)), Quaternion.identity) as GameObject);
                Quaternion rot = new Quaternion();
                rot.eulerAngles = new Vector3(0, 0, 0);
                agentList[i].transform.rotation = rot;
            }
        }
    }

    /*
     * Setting mesh
     * Input : type - the mesh type
     * Output: Chosen mesh
     */
    Mesh SetMesh(string type)
    {
        // Inits:
        Mesh[] meshes = Resources.FindObjectsOfTypeAll<Mesh>();

        // Finding the matching mesh:
        for (int j = 0; j < meshes.Length; j++) {
            if (meshes[j].name == type) {
                return meshes[j];
            }
        }

        return null;
    }

    /*
     * Setting material
     * Input : type - the material type
     * Output: Chosen material
     */
    Material SetMaterial(string type)
    {
        // Inits:
        Material[] materials = Resources.FindObjectsOfTypeAll<Material>();

        // Finding the matching material:
        for (int j = 0; j < materials.Length; j++) {
            if (materials[j].name == type + "Mat") {
                return materials[j];
            }
        }

        return null;
    }



    // Start is called once at the start:
    void Start()
    {
        // Inits:
        enabled = false;
        foodList = new List<GameObject>();
        agentList = new List<GameObject>();

        // Creating socket with ML:
        TcpClient client = new TcpClient();
        IPEndPoint serverEndPoint = new IPEndPoint(IPAddress.Parse(IP), PORT);
        client.Connect(serverEndPoint);
        socket = client.GetStream();

        // Receiving init message:
        string msg = Read();
        InitSim initValues = InitSim.CreateFromJSON(msg);

        // Spawning the environment:
        if (initValues.agentCount > 0 && initValues.foodCount > 0)
        {
            SpawnEnv(initValues);
        }

        // Sending a status message:
        sendStatusMessage();
        enabled = true;
    }

    // Update is called once per frame:
    void Update()
    {
        // Inits:
        enabled = false;
        string msg = Read();
         
        // Condition: finish current generation
        if (msg == "0")
            return;

        // Getting the angle changes:
        angleChange angles = angleChange.CreateFromJSON(msg);
        Write("OK");

        // Condition: next generation
        if (angles.dead)
        {
            // Inits:
            enabled = false;
            string initMsg = Read();

            // Trying to start simulation again:
            try
            {
                InitSim initValues = InitSim.CreateFromJSON(initMsg);
                SpawnEnv(initValues);
                sendStatusMessage();
            }

            catch
            {
                enabled = false;
                return;
            }

            // Setting the flag:
            enabled = true;
            return;
        }

        // Updating food:
        for (int i = 0; i < angles.eaten.Count; i++)
        {
            if (angles.eaten[i] < foodList.Count)
                foodList[angles.eaten[i]].transform.position = new Vector3(Random.Range(-5, 5), 0.8f, Random.Range(-5, 5));
        }

        // Updating agents:
        for (int i = 0; i < agentList.Count; i++)
        {
            if (angles.angles[i] == DEAD_ANGLE_VALUE)
            {
                agentList[i].SetActive(false);
                continue;
            }
            agentList[i].GetComponent<AgentMovement>().move(angles.angles[i]);
        }

        // Sending status message:
        sendStatusMessage();
        enabled = true;
    }

    /*
     * Writing to the ML
     * Input : message - the message
     * Output: < None >
     */
    private void Write(string message)
    {
        byte[] buffer = new ASCIIEncoding().GetBytes(message);
        socket.Write(buffer, 0, buffer.Length);
        socket.Flush();
    }

    /*
     * Getting a message from the ML
     * Input : < None >
     * Output: The message
     */
    private string Read()
    {
        byte[] buffer = new byte[SIZE];
        socket.Read(buffer, 0, SIZE);
        return System.Text.Encoding.Default.GetString(buffer);
    }
}