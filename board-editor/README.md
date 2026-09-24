# Board Editor (first version)

Open **Board Editor.cmd** from the game folder. On this PC the editor has a
private copy of the eight original board archives extracted from your own disc.
For another installation, select **Import from disc…** and choose your own
Europe Rev 2 RVZ plus DolphinTool.exe when prompted.

Choose a board at the top. The top-down view shows every space and its directed
routes. Click a space to edit its type, flags, height, or links. Drag a space
to change its X/Z position. Ctrl+Z/Ctrl+Y undo/redo. **Save project** stores
an editable JSON file. **Export to game** creates `mods/board-edits/data/wXX.bin`
and `board-mods.txt`; launch **Play Edited Boards.cmd** to use it. Starting the
normal executable without that launcher uses the original board archives.

The first version edits the main board-space layer. It preserves the original
archive's other files and the original serialized star markers. It cannot yet
edit terrain models, artwork, camera paths, scripted event behavior, or Toad's
separate coaster route layer. Moving a space visually does not move the scenery
under it. Keep links and event flags consistent with each board's scripted
objects; a valid file can still produce an unplayable route if those disagree.

Board projects need the selected original archive path to export. Do not share
the `original` folder or the resulting `.bin` archives publicly; each player can
extract original files from their own disc and apply the same project edits.
