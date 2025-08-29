# Unity VRM Environment

This folder is a starter Unity project for hosting the Clair avatar.

## Setup
1. Open **Unity Hub** and add this folder as an existing project (Unity 2022 LTS).
2. Install the **UniVRM** package to import `.vrm` models.
3. Drag your VRM file into `Assets/` and open `Assets/Scenes/Main.unity`.
4. Install the [OscJack](https://github.com/keijiro/OscJack) package.
5. Install Unity's **Animation Rigging** package (included in `Packages/manifest.json`).
6. In the Hierarchy, select the avatar root, click **Add Component**, and add
   `PADReceiver` and `IKRigController` (found in `Assets/Scripts/`). Assign the
   avatar's `Animator` and the IK targets/hints to the component. Toggle IK via
   the `enableIK` field or call `SetIKActive` from scripts or Animator layers.
7. The Python app sends PAD values over OSC on port **9000**; with VSeeFace
   running, press Play and the avatar should mirror Clair's emotions.

## Notes
- This project contains no assets by default; import your own VRM.
- See `docs/EXTERNAL_DEPENDENCIES.txt` for detailed setup steps.
