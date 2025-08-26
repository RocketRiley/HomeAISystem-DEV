# Unity Setup Manual

This guide walks through creating the Unity avatar project for Clair from scratch.
It assumes no prior Unity experience.

## 1. Install Unity
1. Install **Unity Hub** from [unity.com/download](https://unity.com/download).
2. In Unity Hub, install **Unity 2022 LTS** (any 2022.3.x release).
3. After installation, open Unity Hub and sign in.

## 2. Open the Project
1. In Unity Hub click **Open** and select the `unity_project/` folder in this repo.
2. When prompted, allow Unity to upgrade any project files.
3. Once loaded you should see the Unity editor with the **Hierarchy**, **Scene**, **Game** and **Inspector** panels.

## 3. Import UniVRM
UniVRM lets Unity read `.vrm` avatar files.
1. Open **Window → Package Manager**.
2. Click the **+** button and choose *Add package from git URL*.
3. Paste `https://github.com/vrm-c/UniVRM.git?path=/Assets/VRMShaders` and press *Add*.
4. After the import completes, Unity can import VRM models.

## 4. Add your VRM Avatar
1. Drag your `.vrm` file into the Project window under `Assets/`.
2. Unity will import it as a prefab; drag the prefab into the **Hierarchy**.
3. Reset the avatar’s position to `(0,0,0)` if needed.

## 5. Install OscJack
OscJack lets the Python runtime drive avatar blendshapes.
1. In **Package Manager**, add `https://github.com/keijiro/OscJack.git` as a git package.
2. After the package loads, Unity provides an `OscReceiver` component.

## 6. Attach the PADReceiver script
1. In the Project window open `Assets/Scripts/` and confirm `PADReceiver.cs` exists.
2. Select the avatar root in the **Hierarchy**.
3. In the **Inspector** click **Add Component** → type `PADReceiver`.
4. Assign the avatar’s `Animator` to the component’s field.

## 7. Configure the Scene
1. Open `Assets/Scenes/Main.unity`.
2. Verify the avatar appears in the Scene view.
3. Ensure there is a camera pointing at the avatar and at least one light source.

## 8. Connect to the Python Runtime
1. Start VSeeFace separately and load the same VRM model (path from `.env` `VSEEFACE_MODEL`).
2. Run the Python launcher: `python -m scripts.ui_launcher` and press **Start Chat**.
3. When conversations occur, the Python app sends PAD values over OSC on port **9000**.
4. With the Unity scene in **Play** mode, the avatar should mirror Clair’s emotions.

## 9. Basic Unity Usage
- **Play Mode**: Press the ▶️ button to run the scene; press again to stop.
- **Moving objects**: Use the W/E/R keys to translate/rotate/scale selected objects in the Scene view.
- **Saving**: Unity auto-saves assets, but press **Ctrl+S** to save the current scene.
- **Building**: From **File → Build Settings**, add `Scenes/Main.unity` and build a standalone app if desired.

## 10. Troubleshooting
- If the avatar does not move, verify VSeeFace is running and `PADReceiver` shows OSC messages in the Console.
- Missing packages can be reinstalled via **Package Manager**.
- For more Unity basics, the [Unity Learn](https://learn.unity.com/) site offers free tutorials.

You can now customise the scene or import additional assets to create a full environment for Clair.
