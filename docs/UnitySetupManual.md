# Unity Setup Manual

## Quick Start

1. Open `Assets/Scenes/Main.unity`.
2. Drag `Clair_Character.prefab` into the **Hierarchy**.
3. Drag `UI_System.prefab` into the **Hierarchy**.
4. Assign your VRM avatar to the `Clair_Character` Animator if needed.
5. Drop a room prefab into the scene and tag interactable objects.
 codex/resolve-conflict-in-readme.md-74x7dq
6. In a terminal, run `python -m scripts.voice_loop_stub` so STT/TTS are
   ready.
7. Press **Play**.
=======
 codex/resolve-conflict-in-readme.md-g7qctv
6. In a terminal, run `python -m scripts.voice_loop_stub` so STT/TTS are
   ready.
7. Press **Play**.
=======
 codex/resolve-conflict-in-readme.md-esoix8
6. In a terminal, run `python -m scripts.voice_loop_stub` so STT/TTS are
   ready.
7. Press **Play**.
=======
 codex/resolve-conflict-in-readme.md-154yk5
6. In a terminal, run `python -m scripts.voice_loop_stub` so STT/TTS are
   ready.
7. Press **Play**.
=======
 codex/resolve-conflict-in-readme.md-ookl8l
6. In a terminal, run `python -m scripts.voice_loop_stub` so STT/TTS are
   ready.
7. Press **Play**.
=======
6. Press **Play**.
 main
main
 main
 main
 main

This guide walks through creating the Unity avatar project for Clair from scratch.
It assumes no prior Unity experience.

## 1. Install Unity

1. Install **Unity Hub** from
   [unity.com/download](https://unity.com/download).
2. In Unity Hub, install **Unity 2022 LTS** (any 2022.3.x release).
3. After installation, open Unity Hub and sign in.

## 2. Open the Project

1. In Unity Hub click **Open** and select the `unity_project/` folder.
2. When prompted, allow Unity to upgrade any project files.
3. Once loaded you should see the Unity editor with the **Hierarchy**,
   **Scene**, **Game** and **Inspector** panels. The project includes
   empty `Assets/CharacterModels/` and `Assets/RoomModels/` folders for
   organising avatars and environments.

## 3. Import UniVRM

UniVRM lets Unity read `.vrm` avatar files.

1. Open **Window -> Package Manager**.
2. Click the **+** button and choose *Add package from git URL*.
3. Paste `https://github.com/vrm-c/UniVRM.git?path=/Assets/VRMShaders`
   and press *Add*.
4. After the import completes, Unity can import VRM models.

## 4. Add your VRM Avatar

1. Drag your `.vrm` file into `Assets/CharacterModels/` in the Project window.
2. Unity will import it as a prefab; drag the prefab into the **Hierarchy**.
3. Reset the avatar's position to `(0,0,0)` if needed.

## 5. Install OscJack

OscJack lets the Python runtime drive avatar blendshapes.

1. In **Package Manager**, add `https://github.com/keijiro/OscJack.git`
   as a git package.
2. After the package loads, Unity provides an `OscReceiver` component.

## 6. Attach the PADReceiver script

1. In the Project window open `Assets/Scripts/` and confirm
   `PADReceiver.cs` exists.
2. Select the avatar root in the **Hierarchy**.
3. In the **Inspector** click **Add Component** -> type `PADReceiver`.
 codex/resolve-conflict-in-readme.md-74x7dq
=======
 codex/resolve-conflict-in-readme.md-g7qctv
=======
 codex/resolve-conflict-in-readme.md-esoix8
=======
 codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
 main
 main
 main
 main
4. Assign the avatar's `Animator` to the component's field. The receiver
   also listens for `/avatar/parameters/MouthOpen` to drive lip-sync, so
   ensure your Animator has a `MouthOpen` float parameter.

## 7. Attach Expression Scripts

1. Add `LipSyncBlendShape.cs` to map the `MouthOpen` animator parameter to
   the avatar's `A` viseme.
2. Add `EmotionBlendShape.cs` to drive facial expressions from the `Joy`,
   `Angry`, `Sorrow`, and `Fun` animator parameters.
3. Add `MicroMotion.cs` for subtle idle movement of the head.

## 8. Configure the Scene
 codex/resolve-conflict-in-readme.md-74x7dq
=======
 codex/resolve-conflict-in-readme.md-g7qctv
=======

 codex/resolve-conflict-in-readme.md-154yk5
=======
=======
 main
 main
 main
 main
 main

1. Open `Assets/Scenes/Main.unity`.
2. Verify the avatar appears in the Scene view.
3. Ensure there is a camera pointing at the avatar and at least one
   light source.

 codex/resolve-conflict-in-readme.md-74x7dq
## 9. Import the Room Environment
=======
 codex/resolve-conflict-in-readme.md-g7qctv
## 9. Import the Room Environment
=======
 codex/resolve-conflict-in-readme.md-esoix8
## 9. Import the Room Environment
=======
 codex/resolve-conflict-in-readme.md-154yk5
## 9. Import the Room Environment
=======
 codex/resolve-conflict-in-readme.md-ookl8l
## 9. Import the Room Environment
=======

 main
 main
main
 main
 main

1. Drag a room model (`.fbx`, `.glb`, `.obj`, `.ply`, etc.) into
   `Assets/RoomModels/`.
2. Add the room prefab to the **Hierarchy** and place the avatar inside it.
3. Adjust the scale and lighting as needed to match the room.

 codex/resolve-conflict-in-readme.md-74x7dq
## 10. Camera and Roaming
=======
 codex/resolve-conflict-in-readme.md-g7qctv
## 10. Camera and Roaming
=======
 codex/resolve-conflict-in-readme.md-esoix8
## 10. Camera and Roaming
=======
 codex/resolve-conflict-in-readme.md-154yk5
## 10. Camera and Roaming
=======
 codex/resolve-conflict-in-readme.md-ookl8l
## 10. Camera and Roaming
=======

 main
 main
 main
 main
 main

1. Attach `LookAtCamera.cs` to the avatar so she faces the main camera while speaking.
2. Attach `RoamController.cs` to enable wandering; bake a NavMesh for the room.
3. Toggle `enableRoam` in the component to let Clair walk around the room.
 codex/resolve-conflict-in-readme.md-74x7dq
=======
 codex/resolve-conflict-in-readme.md-g7qctv
=======
 codex/resolve-conflict-in-readme.md-esoix8
=======
codex/resolve-conflict-in-readme.md-154yk5
=======
 codex/resolve-conflict-in-readme.md-ookl8l
 main
main
 main
 main
4. Add `POIManager.cs` to an empty GameObject to gather objects tagged `Interactable`.
5. Add `CharacterAI_Director.cs` and `IKGrounding.cs` to the avatar to choose
   actions and align feet to the ground.

## 11. Connect to the Python Runtime
 codex/resolve-conflict-in-readme.md-74x7dq
=======
 codex/resolve-conflict-in-readme.md-g7qctv
=======
 codex/resolve-conflict-in-readme.md-esoix8
=======
 codex/resolve-conflict-in-readme.md-154yk5
=======
=======

 main
 main
 main
 main
 main

1. Run the Python voice loop: `python -m scripts.voice_loop_stub`.
2. When conversations occur, the Python app sends PAD values over OSC on
   port **9000**.
3. With the Unity scene in **Play** mode, the avatar should mirror
   Clair's emotions.

 codex/resolve-conflict-in-readme.md-74x7dq
## 12. Basic Unity Usage
=======
 codex/resolve-conflict-in-readme.md-g7qctv
## 12. Basic Unity Usage
=======
 codex/resolve-conflict-in-readme.md-esoix8
## 12. Basic Unity Usage
=======
 codex/resolve-conflict-in-readme.md-154yk5
## 12. Basic Unity Usage
=======
 codex/resolve-conflict-in-readme.md-ookl8l
## 12. Basic Unity Usage
=======
 main
 main
 main
 main
 main

- **Play Mode**: Press the Play button to run the scene; press again to
  stop.
- **Moving objects**: Use the W/E/R keys to translate, rotate, or scale
  selected objects in the Scene view.
- **Saving**: Unity auto-saves assets, but press **Ctrl+S** to save the
  current scene.
- **Building**: From **File -> Build Settings**, add `Scenes/Main.unity`
  and build a standalone app if desired.

 codex/resolve-conflict-in-readme.md-74x7dq
## 13. Troubleshooting
=======
 codex/resolve-conflict-in-readme.md-g7qctv
## 13. Troubleshooting
=======
 codex/resolve-conflict-in-readme.md-esoix8
## 13. Troubleshooting
=======
 codex/resolve-conflict-in-readme.md-154yk5
## 13. Troubleshooting
=======
 codex/resolve-conflict-in-readme.md-ookl8l
## 13. Troubleshooting
=======

 main
 main
 main
 main
 main

- If the avatar does not move, ensure the Python voice loop is running
  and `PADReceiver` shows OSC messages in the Console.
- Missing packages can be reinstalled via **Package Manager**.
- For more Unity basics, the
  [Unity Learn](https://learn.unity.com/) site offers free tutorials.

You can now customise the scene or import additional assets to create a
full environment for Clair.
