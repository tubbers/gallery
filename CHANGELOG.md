# Changelog

Gallery versions are the number in the page footer. Releases before 0.15 were not logged here.

## 0.15 — 2026-10-29
- Several shots of one target. Entries in `gallery.json` that share a `group` show as one tile on the grid. The tile shows the `lead` version, or the newest by `captured` if no lead is set. The tile caption says "2 versions" and "▶ video" where they apply.
- The lightbox has a thumbnail strip along the bottom of the photo with every version and its video. Clicking a thumbnail swaps the photo and the facts panel (telescope, camera, place and date belong to the version). ↑/↓ also step through the versions.
- Each version keeps its own slug, so an existing `#the-sun` link still works: it opens the target with that version on show.
- Prev/next (‹ ›, ←/→) now step between targets, not versions. On a touch screen a horizontal swipe on the un-zoomed photo does the same.
- Video: a manifest entry can carry `video` (H.264 MP4) and `poster`. It plays muted, looped and inline (iOS too), and the download stops when you move away. The Moon comparison is hidden while the video is on show.
- `DWARF Mini` (150 mm) added to the telescope list.
- Local preview only: on localhost, `?skydome=/path/` points the page at a scratch copy of skydome. The public site ignores it.
- First grouped target: The Sun (ISS transit 2026, DWARF Mini, lead; ISS transit 2025, Seestar S50).
