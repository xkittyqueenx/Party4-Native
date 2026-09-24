# Mario Party 4 Deluxe playtest notes

Status: development build, 23 September 2026. Full original-game fidelity is not yet verified.

Launch **Mario Party 4 Deluxe.exe** directly. You can report issues as you find them; you do not need to complete a checklist first.

## What has been checked

- All six boards completed five-turn automated matches. Those earlier tests did not include the award ceremony.
- 61 minigame catalogue entries reached results and exited cleanly with CPU or scripted input. This does not verify every win/loss path, controls, graphics, sound, or rule. Two additional catalogue entries map to the same overlay and remain unclassified.
- The 99-round minigame reached score 99, finished, and exited cleanly.
- The reported idle-menu crash was reproduced as a GPU texture-allocation leak, fixed, and retested for 150 seconds with the same graphics settings. Longer idle sessions still need testing.
- The results controller selector passed guarded-array checks for 10,000 human/CPU and port configurations. A corrected Goomba-board run then completed five turns, the original award ceremony, final results, and a clean exit without a crash or overlay-history error. Other boards' complete endings still need verification; this is not visual or audio verification of the ceremony.

## Areas needing playtesting

| Area | What to look for |
| --- | --- |
| Full matches | Board events, bonus stars, final rankings, award ceremony, and returning to menus |
| Widescreen | HUD cards, roulette text, purple instruction bars, transitions, and characters near the edges |
| Minigames | Controls, practice/retry, team assignments, wins, losses, ties, and results |
| Sound | Missing or incorrect effects/music, cut-offs, and volume changes |
| Saves | Saving through the original menus, quitting, and loading the same progress |
| Text | Accents, clipped letters, spacing, and readability with the supplied upscaled font |

Online multiplayer is not yet validated. A local automated test does not establish online readiness.

## Reporting an issue

Send whatever information you have. The most useful details are:

- Board/minigame/menu and the steps immediately before the issue.
- What happened and what you expected instead.
- Whether it happens every time or only occasionally.
- Screenshot or short clip, especially for animation/layout problems.
- Controller type and graphics settings if they seem relevant.
- For a crash, approximate time and any crash-report filename.

Optional copyable format:

```text
Location:
Steps:
Actual result:
Expected result:
Repeatable?:
Screenshot/clip/crash report:
```

Keep the original report until a fix has been retested. “Fixed in code” and “confirmed fixed while playing” are separate statuses.
