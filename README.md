# Mario Party 4 Deluxe — native PC development build

Launch **Mario Party 4 Deluxe.exe** directly. Play.exe is an optional, limited party/practice launcher; it is not required for the normal game.

The current target is the complete original Mario Party 4 experience for testing before adding new boards, characters, minigames, or gameplay changes. The normal executable exposes the original game modes and content. Full-game compatibility has not yet been verified.

See [playtest notes](PLAYTESTING.md) for current verification limits and a simple issue-report format.

This build includes:
- Mario Party 4 Deluxe window and PC menu branding. The Play / Settings / Play Online menu appears before starting the game.
- The original title screen keeps its Nintendo / HUDSON SOFT notices and adds Deluxe PC edition: xStrawbewwy underneath. These additions disappear when leaving the title screen. Original Party Board foundation credits are retained in this document.
- After pressing Play, company logos and the opening movie are skipped, bringing you to the original title screen. Start continues to the original save-selection flow. Turn off **Skip Game Boot Sequence** in settings to restore the original startup sequence. The patterned DELUXE wordmark appears beneath the original logo on the title screen and PC menu. The first run still needs your own disc image and may require language selection.
- Native music and sound enabled, with working master volume.

Use the native Video settings to select internal resolution and adaptive widescreen. These are optional; original aspect ratio is still available. The game uses the assets from your own local disc image, which is not included or modified.

**Smooth Character Animations** is off by default in Video settings. If enabled with the frame-rate setting above 60 FPS, it samples the original skeletal animation curves between simulation frames, including animation blending. It does not raise the gameplay simulation rate or upscale sprite animation frames. An existing profile that explicitly saved this setting as on keeps that choice; switch it off in Video settings if desired.

Normal direct launches keep the existing Party Board settings and saves. The optional Play.exe uses its own profile. Esc/F1 opens native settings. Play Online now launches an English-language experimental companion and accepts the Europe Rev 2 disc. The companion currently supports two PCs and has not been verified in a real two-PC session; four-player hosting remains in development.

Online hosting currently tries automatic direct connections through PCP, NAT-PMP, then UPnP. If your router rejects all three, the lobby explains this in English and suggests letting the other player host. A relay or Steam-style fallback is not implemented yet, so some networks cannot host directly.

Based on [Party Board](https://github.com/mariopartyrd/partyboard) and the [zeranemesis fork](https://github.com/zeranemesis/Marioparty4), base commit 8d27ee358df5646a2321e94371654db79a636651. Original game content belongs to its original owners; xStrawbewwy is credited for the Deluxe PC changes, not original game authorship.




## Visual style rule
All additions should belong to the original game's visual language: native game UI, matching lettering, consistent outlines, spacing and animation. The title's DELUXE artwork is imported as a cropped 224x56 GameCube sprite. The credit uses the native game font and window renderer. Neither is drawn as a desktop-resolution overlay. The original copyright notices remain intact. The PC menu uses the same patterned source wordmark with its transparent padding cropped at draw time. Western dialogue now uses the user-supplied 4x font atlas by default, retaining the original layout and colours; it falls back to the original atlas if the replacement is unavailable. Japanese text and decorative minigame headings use their separate original assets.

Adaptive widescreen keeps the main menu layouts on a shared centered coordinate canvas while the 3D view widens. This prevents independently shifted icons, labels and panels. Layout arithmetic is checked at 4:3, 16:9 and 21:9; every individual menu has not yet been visually verified.

Latest menu fixes (23 September 2026)
- Native xStrawbewwy title credit survives the intro cleanup and language changes.
- Title background fills adaptive widescreen; original-aspect mode remains available.
- Party character-select portraits, panel border and button labels now align at16:9.
- Title screen stays open when idle instead of restarting its intro.
Title and character-select were visually checked at2560x1440. Other menus still need a complete visual audit; this is not a claim that the entire original game is finished.

The DELUXE wordmark and native PC credit now use the original title logo's entrance zoom and fade. Both settle at their existing size and position.

Optional visual enhancements are planned after the original-game baseline. Original visuals remain available. Lossless Scaling may be used as a separate companion in a supported window mode, but compatibility has not yet been tested; its proprietary technology is not included in this build. Built-in AI upscaling and enhanced texture packs are not implemented.
File selection and mode selection now expand their background sprites and remove the original safe-frame border when adaptive widescreen is enabled. The patch is installed; visual verification of these two screens is still pending. Original framing is retained when adaptive widescreen is disabled.
Menu transition update: the two prerecorded file/mode transitions now fill the adaptive widescreen canvas. Dismissed memory-card boxes move beyond its wider edge. The remaining top/bottom background gaps are filled too. Mode-selection introduction was visually confirmed edge-to-edge; complete transition motion still needs visual verification.

Host lineup update: Board selection now runs left-to-right as Toad, Shy Guy, Boo, Koopa, Goomba, Koopa Kid. Bowser's Gnarly Party is available from the start and shares the selection row. Save completion progress is preserved. Build/install verified; please report any layout or selection issues during playtesting.

Stage spacing update: Removed the old Bowser direction signs and widened the stage by 20% while preserving host and UI sizes. Also fixed a reproduced Toad item-carousel animation-loading crash; eight repeated native initialization/cleanup cycles passed. Full event playthrough verification remains pending.

Toad's Midway Madness teacups now offer a fresh exit choice on every ride. Point the stick toward an arrow and press A to confirm; the larger arrow is selected. CPU players choose automatically. The arrow no longer automatically flips after a ride. The original happening-space arrow animation remains, but cannot force your next route. Both installed copies are updated; controller/visual playtesting is still needed.

Smooth animation adjustment: animated scaling and its transition blend now retain the original timing to address reported eyelid expansion. Position and rotation smoothing remain enabled by default. Yoshi's happy expression still needs visual confirmation.

Latest update: The two obsolete teacup direction landing spaces on Toad's Midway Madness are now blue spaces. The teacup choice remains available before each ride. Minigame results backdrops now cover 16:9 in both standard and battle results. Booksquirm keeps its book and falling-page pieces on the original frame timing at higher display frame rates, addressing the brief extra-book flash reported above 60 FPS. Please verify the results layout and Booksquirm visually; automated checks cover the board conversion and minigame completion, not those exact images. Mega players can visit the current star host using the usual purchase dialog.

Bowser-space update: Bowser now appears on every Bowser-space landing, without Koopa Kid. His random outcomes include 10, 15, 20, or 30 coins; half of the active player's coins (rounded up); ten coins from every player; one Star; Bowser Minigame; Revolution; and Shuffle. Payments never take more coins than a player holds, and Bowser leaves angrily when the active player has no coins or Star to surrender. Bowser Minigames can be selected at zero coins; the loser loses half their coins or all items. A no-loser result has no penalty. The new dialogue uses the game's own Bowser portrait/window renderer. These rules replace the original Bowser-space rules in this development build; the planned original-rules option is not yet present. Event UI and a full human Bowser-space playthrough still need visual testing.

Item-space update: Each gift box can now reveal a Mini Mushroom, Mega Mushroom, Warp Pipe, Sparky Sticker, MiniMega Hammer, Chomp Call, Swap Card, Super Mega Mushroom, or Super Mini Mushroom. The nine outcomes are equally likely. The revealed original model, inventory item, and native-style item message use the same selected item ID. The tutorial still demonstrates the two original mushrooms. Full human-controller visual verification remains pending.

Mega visit update: While walking with Mega active, you can stop at the current Star host, shop, Boo House, or Lottery House. The character quickly shrinks to normal size for the interaction, then grows back to Mega afterward, including when you decline or leave. A Star still uses the normal 20-coin purchase choice. This path passed isolated route tests; a controller playthrough of all four events is still pending.

Shop update: The native PC shop now offers six items plus Return. The item rows use the game's own price text without a duplicated price column, and the list no longer has an overlapping host portrait. The extra boards use the same varied stock; Magic Lamps are excluded there because they have no Star. The shop crash caused by a PC menu message being read as a disc message has been fixed. The six-row message construction and native build passed checks; please report any remaining spacing issues in play.

Mega Mushroom descriptions now explain that Mega characters can still visit Stars, shops, lotteries, and Boo Houses while moving. The description is updated in the shop and item inventory for Mega and Super Mega Mushrooms.

Bowser Phone test item: During a local board game, open Settings > Cheats > Give Bowser Phone to add one to the current player's empty inventory slot. The phone now has its own low-poly 3D model as well as its native-resolution HUD artwork. When used, the player holds the phone and calls Bowser; Bowser asks whom to visit. Choose any player or let him pick one. The board camera then follows the chosen player for the event. The phone is currently debug-only and excluded from random item rewards and online play. A full controller playthrough of the model, hand placement, and camera remains necessary.

Bowser event reveals: the original BOWSER GAME, Shuffle, and Revolution title sprites remain intact. Every added coin and Star outcome now has a matching 256×80 native sprite in the same three-layer pop-in reveal, including BOWSER WANTS COINS, BOWSER TAKES HALF, EVERYONE PAYS, and LOSE A STAR. Coin and Star dialogue now waits for a button press. The art and event logic are installed; these new reveals still need an in-game visual check.

Bowser Phone crash fix: a procedural model attached to the player's hand is now queued through the renderer's model-hook path instead of being interpreted as a disc HSF model. The reported crash trace showed that incorrect HSF read. The compact HUD phone artwork now preserves its portrait proportions when reduced to the native 48×48 sprite canvas. The expanded item picker uses the phone's 3D model, as it does for other items; its size and hand position still need visual confirmation in play.

Take a Breather update: Its water-stage projection now uses the same widescreen aspect as the scene camera, and the timer/record digit spacing is tighter at widescreen resolutions. These visual changes have not yet been confirmed in a live minigame capture.
