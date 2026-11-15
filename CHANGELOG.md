# Changelog

Gallery versions are the number in the page footer. Releases before 0.15 were not logged here.

## 0.22 — 2026-11-15
- Click a constellation, discoverer or telescope in the detail view and a picture pops up on the page: the IAU constellation chart, the discoverer's portrait (with the year, a credit and a link to Wikipedia) or Wade's own photo of the telescope. It closes with ✕, Esc or a click outside, and works on phones.
- New "Constellation" row in the facts list. Six images that had no discoverer listed now show one.
- All the popup pictures live in this repo under `assets/` (38 constellation charts, 21 portraits, 7 telescope photos, about 5.5 MB). `assets.json` maps them to the gallery: telescope photos by the `scope` field, with the Nebula Nest photo for `"site": "nebula-nest"` images.
- Discoverers without a free portrait show a placeholder image (`assets/people/default_discovery.jpg`) for now.
- Credits for the charts and portraits are in `credits.md` and behind a new link in the footer.

## 0.21 — 2026-11-15
- Corrected capture details for NGC 1365 (one night at Parkes, 18 October 2025, 5.3 hours, unfiltered one-shot colour), the wider NGC 3572 / Gum 37 version (200PDS, not ASKAR 91F; same 14–16 April 2026 data as the Southern Tadpoles) and LDN 1688 Rho Ophiuchi (two-panel RedCat 61 + ASI2600MM RGB mosaic, Wheeny Creek, 11–13 August 2026, 9.2 hours).
- Added an approximate capture date (December 2024) to the Seestar Horsehead, Wade's first deep-sky image.

## 0.20 — 2026-11-14
- Added NGC 1532 (Haley's Coronet), an edge-on barred spiral in Eridanus with its dwarf companion NGC 1531, captured from Wheeny Creek and Wiruna (200PDS + ASI585MC, 10 hours, 11 October and 5 November 2026).
- Added M 74 (NGC 628, the Phantom Galaxy), a face-on grand design spiral in Pisces, captured from Wiruna (200PDS + ASI585MC, 12 hours, 6–8 November 2026).

## 0.19 — 2026-11-13
- Added NGC 1097 (Caldwell 67), a barred spiral in Fornax, captured from Wiruna (200PDS + ASI585MC, 11 hours, 5–8 November 2026).
- Rewrote the M31 and M78 gallery blurbs in the older educational style: the science and what to look for, with a short capture line, and without processing step lists.


## 0.18 — 2026-11-13
- Added M31 Andromeda Galaxy (DWARF Mini, Wiruna, 5–8 November 2026) and M78 (NGC 2068) (Askar 91F, Nebula Nest).
- Optional `site` field in `gallery.json`. Set `"site": "nebula-nest"` to show the Nebula Nest logo as a badge on the grid card and in the detail view, linking to https://nebulanest.com.au. Reuse it on future Nest images.
- New thumbnails are 1,200 px on the long side (`web/thumbs/<name>_1200.jpg`). Existing 1,024 px thumbs are unchanged.

## 0.17 — 2026-10-29
- Added the Crescent Nebula (NGC 6888), Cygnus.

## 0.16 — 2026-10-29
- Four more targets are grouped into one tile each, with a version strip. Every existing slug still opens its own version.
  - **M8 Lagoon** (`m8-lagoon`): lead `lagoon-lh` (SHO, 2026), plus `m8-lagoon-nebula` (2025). The Lagoon + NGC 6559 wide field stays separate.
  - **NGC 6188 Fighting Dragons** (`ngc-6188`): lead `ngc-6188-fighting-dragons-hoo`, plus `ngc-6188-fighting-dragons-sho`.
  - **Southern Tadpoles** (`ngc-3572-gum-37`): lead `ngc-3572-gum-37` (Askar 91F), plus `ngc-3572-gum-37-southern-tadpoles` (200PDS). The Tadpoles + Statue of Liberty wide field stays separate.
  - **NGC 346** (`ngc-346`): lead `ngc-346-smc` (200PDS), plus `smc-core-ngc-346-region-hoo` (Askar 91F).
- Added NGC 460 (N84), Small Magellanic Cloud.
- Fixed the filters on NGC 6188 Fighting Dragons (HOO): Ha/OIII.

## 0.15 — 2026-10-29
- Several shots of one target. Entries in `gallery.json` that share a `group` show as one tile on the grid. The tile shows the `lead` version, or the newest by `captured` if no lead is set. The tile caption says "2 versions" and "▶ video" where they apply.
- The lightbox has a thumbnail strip along the bottom of the photo with every version and its video. Clicking a thumbnail swaps the photo and the facts panel (telescope, camera, place and date belong to the version). ↑/↓ also step through the versions.
- Each version keeps its own slug, so an existing `#the-sun` link still works: it opens the target with that version on show.
- Prev/next (‹ ›, ←/→) now step between targets, not versions. On a touch screen a horizontal swipe on the un-zoomed photo does the same.
- Video: a manifest entry can carry `video` (H.264 MP4) and `poster`. It plays muted, looped and inline (iOS too), and the download stops when you move away. The Moon comparison is hidden while the video is on show.
- `DWARF Mini` (150 mm) added to the telescope list.
- Local preview only: on localhost, `?skydome=/path/` points the page at a scratch copy of skydome. The public site ignores it.
- First grouped target: The Sun (ISS transit 2026, DWARF Mini, lead; ISS transit 2025, Seestar S50).
