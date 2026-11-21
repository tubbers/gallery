# Changelog

Gallery versions are the number in the page footer. Releases before 0.15 were not logged here.

## 0.30 — 2026-11-21
- Bring the shorter object descriptions in line with Andromeda: readable science, visual cues and no capture settings in the prose.
- Correct the classification of the Gem Cluster, the Dragon’s Egg, Thor’s Helmet and the Dolphin Head.

## 0.29 — 2026-11-21
- Use month-level capture dates; keep photography details in the Gallery facts table.

## 0.28 — 2026-11-21
- Added M33, the Triangulum Galaxy, captured from Wiruna (GSO 150 + ASI2600MM, LRGB, 7.17 hours of integration over November 2026).

## 0.27 — 2026-11-18
- Added NGC 6752 (the Great Peacock), a globular cluster in Pavo, captured from Wiruna (GSO 150 + ASI2600MM, LRGB, 1.46 hours over November 2026). The GSO 150 telescope photo now appears on this image.
- Added NGC 1433, a barred spiral in Horologium with Type Ia supernova SN 2026ahvu just above and to the right of the core, captured remotely from the Nebula Nest on November 2026 (Askar 91F + ASI2600MC, 1.15 hours). It has the Nebula Nest badge and the observatory photo, like M 78.
- Added the IAU chart for Horologium (CC BY 3.0, the 39th constellation chart).
- The Galaxies filter now includes barred spirals, and a new Clusters filter covers globular and open clusters. Neither image has narration yet, so the speaker and “Hear about it” button stay hidden on them.

## 0.26 — 2026-11-15
- Every image now has a five-part narration: the intro, the discoverer, the science (with the to-scale Moon for the first four seconds), the telescope, and a closing line that leaves the photo clear. The speaker icon on the photo still starts and stops it.
- A new "Hear about it" button sits in the details, next to "See where it is", in the same style, so the narration is easier to find. It plays and stops the same recording, and only shows when there is one to hear. It works on phones as well as on a desktop.

## 0.25 — 2026-11-15
- Integration times on the page now use the hours that went into the final stack, wherever the capture tracker has that figure. Captured-but-not-stacked totals and times that only lived in the gallery are unchanged. Nights were brought into line with the same records, so the page and the narration scripts agree. Forty-three images changed; nine already matched.

## 0.24 — 2026-11-15
- Narration test on M 74 (the Phantom Galaxy). A speaker button sits with the other photo tools: tap it to hear the four-part narration (intro, discoverer, the science, the telescope), tap again to stop. It glows softly while playing. Voice: Google TTS en-AU-Chirp3-HD-Callirrhoe.
- While it plays, the picture card follows along: the Pisces chart during the intro, Pierre Méchain during the discoverer part, the to-scale full Moon over the photo for the first four seconds of the science part, then the 200PDS during the telescope part. Everything clears when it finishes, when you stop it, move to another image or close the photo.
- It only starts from a tap (phones need that), skips any part whose file is missing, and loads the next part while the current one plays.
- Narration is data only: a `narration` entry for an image's label in `assets.json`, with the clips in `audio/`. The speaker shows only on images that have one, so just M 74 for now.
- The picture card is 50% bigger on desktop (375 px wide). Phones are unchanged.

## 0.23 — 2026-11-15
- The constellation, discoverer and telescope pictures now open as a small card in the bottom-right corner of the photo, about half the old size, instead of a dialog over the image. There's no dimmed backdrop, so the photo, the arrows and the details panel all stay visible and usable. Clicking another fact swaps the card; ✕ or Esc closes it, and it closes by itself when you move to another image. On phones it is a compact strip below the arrows.
- Added portraits for Bernard Mills and Beverly Lynds (AIP Emilio Segrè Visual Archives, John Irwin Slide Collection, Attribution licence via Wikimedia Commons). Every portrait card has a source link.
- Royal Frost still shows the placeholder: the only known portrait is on a site that could not be reached when this was built.
- For future automation: `showAsset(kind, key)` and `hideAsset()` open and close the card from script. `kind` is `constellation`, `discoverer` or `scope`; `key` is a name (or a longer phrase containing one, as in the narration cues), or can be left out to use the image on show.

## 0.22 — 2026-11-15
- Click a constellation, discoverer or telescope in the detail view and a picture pops up on the page: the IAU constellation chart, the discoverer's portrait (with the year, a credit and a link to Wikipedia) or Wade's own photo of the telescope. It closes with ✕, Esc or a click outside, and works on phones.
- New "Constellation" row in the facts list. Six images that had no discoverer listed now show one.
- All the popup pictures live in this repo under `assets/` (38 constellation charts, 26 portraits, 8 telescope photos, about 6 MB). `assets.json` maps them to the gallery: telescope photos by the `scope` field, with the Nebula Nest photo for `"site": "nebula-nest"` images. The GSO 150 photo is in place for future images.
- Most portraits are public domain or Creative Commons. Five (DeLisle Stewart, John Bevis, Robert McNaught, Stewart Sharpless, Aage Sandqvist) are © their source and used with credit. The three people still without one (Royal Frost, Bernard Mills, Beverly Lynds) show a placeholder image (`assets/people/default_discovery.jpg`).
- Credits for the charts and portraits are in `credits.md` and behind a new link in the footer.

## 0.21 — 2026-11-15
- Corrected capture details for NGC 1365 (one night at Parkes, October 2025, 5.3 hours, unfiltered one-shot colour), the wider NGC 3572 / Gum 37 version (200PDS, not ASKAR 91F; same April 2026 data as the Southern Tadpoles) and LDN 1688 Rho Ophiuchi (two-panel RedCat 61 + ASI2600MM RGB mosaic, Wheeny Creek, August 2026, 9.2 hours).
- Added an approximate capture date (December 2024) to the Seestar Horsehead, Wade's first deep-sky image.

## 0.20 — 2026-11-14
- Added NGC 1532 (Haley's Coronet), an edge-on barred spiral in Eridanus with its dwarf companion NGC 1531, captured from Wheeny Creek and Wiruna (200PDS + ASI585MC, 10 hours, October and November 2026).
- Added M 74 (NGC 628, the Phantom Galaxy), a face-on grand design spiral in Pisces, captured from Wiruna (200PDS + ASI585MC, 12 hours, November 2026).

## 0.19 — 2026-11-13
- Added NGC 1097 (Caldwell 67), a barred spiral in Fornax, captured from Wiruna (200PDS + ASI585MC, 11 hours, November 2026).
- Rewrote the M31 and M78 gallery blurbs in the older educational style: the science and what to look for, with a short capture line, and without processing step lists.


## 0.18 — 2026-11-13
- Added M31 Andromeda Galaxy (DWARF Mini, Wiruna, November 2026) and M78 (NGC 2068) (Askar 91F, Nebula Nest).
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
