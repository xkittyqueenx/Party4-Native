# Bowser Phone art and model

- `bowser-phone-art.png`: AI-generated transparent artwork based on the supplied phone reference. The installed game downsamples this to a 48×48 native HUD sprite.
- `bowser-phone.obj` and `bowser-phone.mtl`: an AI-assisted low-poly mesh with a chamfered green case, gold screen bezel, white spikes, Bowser emblem, buttons, speaker holes, and side switch. The OBJ uses 315 vertices and 257 faces; import both files together into a 3D editor.
- `bowser-phone-model-preview.png`: flat-shaded preview of that mesh.

The game currently uses the new HUD sprite, while the 3D item display still uses a temporary Bowser Suit model. The OBJ needs conversion to the game's HSF model format and animation binding before it can replace that display safely.
