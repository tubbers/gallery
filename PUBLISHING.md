# Publishing a new image

How a finished JPEG becomes a live entry on **skydome** and **gallery**.

Skydome is the source of truth. The gallery reads skydome's `manifest.json` at page
load and joins it to its own `gallery.json` on the `label` field. Add an image to
skydome and it appears in the gallery immediately, with no gallery change at all —
it just shows less until `gallery.json` catches up.

> Written for whoever automates this. The exact script names below are Wade's
> existing tools; this document defines the **contract** each step has to satisfy,
> not the internals of those scripts.

---

## Repositories

| Repo | Live at | Holds |
|---|---|---|
| `tubbers/skydome` | `tubbers.github.io/skydome/` | images, `manifest.json`, the dome viewer |
| `tubbers/gallery` | `tubbers.github.io/gallery/` | `index.html`, `gallery.json`, logos, `moon.png` |

Working copy on the PC: `C:\Astro\scripts\skyplan\Images` maps to the skydome repo root.

```
skydome/
├── manifest.json
├── index.html                    v1.4.0
├── moon.png  sky.jpg  smoke.js
├── <original>.jpg                full-size masters, any size
└── web/
    ├── display/<name>_2400.jpg   long edge 2400px
    └── thumbs/<name>_1024.jpg    long edge 1024px (existing images)
        └── thumbs/<name>_1200.jpg    long edge 1200px (new images, from 13 Nov 2026)
```

---

## The five steps

### 1. Drop the master in the skydome repo root

Full-resolution processed JPEG, named however you like. The filename becomes the
`original` field and is the stable identity of the image — labels are editorial and
can change, filenames should not.

Avoid spaces. 17 existing files have them and they work, but only because the site
URL-encodes each path segment. New files should use hyphens.

### 2. Generate the two web sizes

Long edge **2400px** into `web/display/` (suffix `_2400`). Thumbnails go in `web/thumbs/`:
**1200px** on the long side for new images (suffix `_1200`). Existing thumbnails stay at
**1024px**. Quality 85–90 is plenty; these are display copies.

Do not crop or rotate at this stage — see the warning under step 3.

### 3. Plate solve → `manifest.json`

`solve_dso.py`. Must write one object per image into `manifest.json` → `images[]`:

**Required**

| Field | Notes |
|---|---|
| `original` | master filename, with extension |
| `file` | `web/display/<name>_2400.jpg` |
| `thumb` | `web/thumbs/<name>_1024.jpg` or `web/thumbs/<name>_1200.jpg` (new images use 1200) |
| `label` | display name, e.g. `NGC 6960 Veil Nebula`. **Must be unique.** |
| `slug` | slugified label. Gallery and dome both key links off this. |
| `solved` | `true`. Anything `false` is skipped by the gallery. |
| `ra_deg` `dec_deg` | centre, degrees |
| `fov_w_deg` `fov_h_deg` | field, degrees — drives the Moon comparison |
| `pixscale_arcsec` | arcsec/pixel — **also identifies the rig, see below** |
| `width_px` `height_px` | of the display JPEG |
| `corners` | 4 × `[ra, dec]` for the dome footprint |

**Optional but wanted**

`distance_ly` (string, comma-grouped, e.g. `"2,360"`), `distance_note` (the actual
citation), `constellation`, `discovered_by`, `discovered_year`, `description`.

**Video (optional):** `video` (repo-relative path to an H.264/yuv420p MP4 with
faststart, under `web/video/`) and `poster` (a JPEG frame). Source GIFs and
MPEG-4 Part 2 files don't play everywhere, so re-encode them first:

```bash
ffmpeg -i in.mp4 -map_metadata -1 -c:v libx264 -profile:v high -pix_fmt yuv420p \
  -crf 20 -preset slow -movflags +faststart -an web/video/<name>.mp4
```

**The Sun (no plate solve possible):** add a `hints.json` entry beside the master
instead of solving. `solve_dso.py` 1.15.0 measures the disc and writes the geometry
(`engine: "ephemeris"`, `track: "sun"`, an `ephem` block), and the dome then follows
the live Sun:

```json
{"my-sun.jpg": {"ephemeris": "sun", "epoch_utc": "2026-10-17T06:45:00Z",
                "pa_up_deg": 122.5, "orientation": "horizon", "blend": "screen",
                "label": "ISS transit of the Sun"}}
```

`pa_up_deg` is the position angle of image-up at capture. Measure it by matching
the sunspots to an SDO/HMI image from that time, or for an alt-az, zenith-up frame
use the parallactic angle. Avoid "Solar", "Jup", "Mars", "Saturn" and "Moon" in
the filename. Those names mean gallery-only, no geometry.

> **Solve the same pixels you publish.** The gallery infers the telescope and camera
> from `pixscale_arcsec`, and the Moon overlay scales off `fov_w_deg`. If the solve
> is run on a different crop or resolution than the file in `web/display/`, both
> silently go wrong. Solve the 2400px display copy, or solve the master and make the
> display copy a pure uncropped downscale.

### 4. Commit skydome

```bash
cd <skydome>
git add .
git commit -m "Add <label>"
git push
```

Live in about a minute. **The image is now in the gallery too** — name, distance,
constellation, description, framing, Moon button, dome link. Only the capture
details are missing.

### 5. Add the capture details to `gallery.json`

One object, keyed on the exact `label` from the manifest. Every field optional.

```json
{
  "label": "NGC 6960 Veil Nebula",
  "scope": "RedCat 61",
  "camera": "ASI2600MC",
  "filters": "Ha/OIII (ALP-T)",
  "location": "Willoughby",
  "bortle": 7,
  "hours": 49.2,
  "nights": 14,
  "captured": "2026-05-30 to 2026-08-08",
  "amp_id": 165,
  "amp_slug": "c63-ngc-7293-helix-eye-of-god-planetary-nebula",
  "favourites": 3,
  "astrobin_likes": 19,
  "telescopius_likes": 7,
  "downloads": 85,
  "reprocessed": 5,
  "blurb": "Public-facing description, 3–4 sentences.",
  "type": "Supernova Remnant",
  "featured": true
}
```

Then commit the gallery repo the same way.

---

## Field reference for `gallery.json`

Raw values only. The site formats them for display — don't pre-format here or the
plate-scale tooling breaks.

| Field | Values |
|---|---|
| `scope` | `200PDS` · `ASKAR 91F` · `RedCat 61` · `RedCat 51` · `Pentax 135mm`. Focal length is added by the site. |
| `camera` | `ASI585MC` · `ASI2600MC` · `ASI2600MM` · `ASI1600MM`. The site appends "(mono)" to the MM bodies. |
| `filters` | Free text. `Broadband` and `OSC broadband` both render as "None". |
| `location` | `Willoughby` · `Wheeny Creek` · `Wiruna` · `Parkes` · `Capertee Valley` · `Nebula Nest, Vic` |
| `bortle` | integer |
| `hours` | decimal, total integration for **this image** |
| `nights` | integer, distinct dates |
| `amp_id` / `amp_slug` | from the AstrophotoMarket URL: `/en/image-details/<id>/<slug>` |
| `favourites` | AstrophotoMarket hearts |
| `astrobin_likes`, `telescopius_likes` | added to `favourites` for the ♥ total |
| `downloads` | the **Sales** column, not Downloads — Downloads counts repeat pulls by the same person |
| `reprocessed` | the Community column |
| `blurb` | overrides the manifest `description` |
| `type` | overrides the coordinate-matched type. Buckets: Nebulae, Galaxies, Dust & dark, Remnants |
| `featured` | `true` makes it a banner candidate; several flagged rotates between them |
| `group` | stable key (slug form) shared by several shots of one target, e.g. `the-sun`. They show as one tile with a version strip in the lightbox. Never rename it once published. |
| `lead` | `true` on the version the grid shows and a click opens first. Default: newest `captured`. |
| `site` | Optional. `nebula-nest` marks the card and the detail view with the Nebula Nest logo (`nest-logo.png`), linking to https://nebulanest.com.au with the title and alt text “Captured at the Nebula Nest”. Reuse this on every future image taken at the Nest. Other values are ignored. |
| `wallpaper` | URL to a 3840×2160 crop, if one exists |
| `_check` | free-text notes to yourself. Ignored by the site. |

---

## Working out the rig from the plate scale

`arcsec/px = 206.265 × pixel_size_µm ÷ focal_length_mm`

| | ASI585MC 2.9µm | ASI1600MM 3.8µm | ASI2600 3.76µm |
|---|---|---|---|
| 200PDS 950mm | 0.630 | 0.825 | 0.816 |
| Askar 91F 609mm | 0.982 | 1.287 | 1.274 |
| RedCat 61 300mm | 1.994 | 2.613 | 2.585 |
| RedCat 51 250mm | 2.393 | 3.135 | 3.102 |
| Pentax 135mm | 4.431 | 5.806 | 5.745 |

Match `pixscale_arcsec` to the table. Two caveats:

- **RedCat 61 + 1600MM (2.613) and RedCat 61 + 2600 (2.585) differ by 1%.** Break
  the tie on sensor aspect ratio: 585MC is 1.78, 1600MM is 1.32, 2600 is 1.50.
- **Drizzled or resampled files land off the table by a clean factor.** Divide the
  theoretical scale by the observed one; 2.00 means 2× drizzle, 0.78 means the file
  was downscaled. The ratio should be close to a simple number — if it isn't, the
  solve and the published file probably don't match.

Validated against 7 known rigs: 6 correct.

---

## Popup pictures (`assets.json`, from v0.22)

The detail view's Constellation, Discovered and Telescope values open a small picture card
docked in the bottom-right corner of the photo (v0.23). Script can drive the same card:
`showAsset("constellation" | "discoverer" | "scope", key)` and `hideAsset()`. `key` is
matched against the names and `aliases` in `assets.json` (a phrase that contains a name also
matches, so narration cue strings work as they are); leave it out to use the image on show.
Everything is in this repo, so nothing is hotlinked at runtime.

| Key in `assets.json` | Holds |
|---|---|
| `scopes` | one entry per `gallery.json` `scope` string → `assets/scopes/<file>.jpg`, plus `aliases` |
| `site_scopes` | per-`site` override, e.g. `nebula-nest` + `ASKAR 91F` → `nebula.jpg` |
| `constellations` | IAU chart PNG, credit, Commons source, Wikipedia link |
| `people` | portrait file (or `null` for the placeholder), credit, licence, source, Wikipedia link, optional `aliases` |
| `labels` | per gallery `label`: `constellation`, `person`, `year`, optional `caption`, `discovered_text`, `constellation_text`, `show_person` |
| `fallback` | the placeholder portrait, `assets/people/default_discovery.jpg` |

**A new image:** add a `labels` entry keyed on its exact label. If it uses a new scope,
constellation or person, add that too: constellation charts are commons
`File:<Name>_IAU.svg` rendered to a 1,200 px wide PNG, and portraits should be public
domain or CC-licensed (anything else only with Wade's OK, credited to its source), about 600 px tall, with the credit recorded. Then list the file in
`credits.md`. Strip EXIF from any phone photo before adding it.

---

## Checklist

- [ ] Master JPEG in skydome root, no spaces in the filename
- [ ] `web/display/<name>_2400.jpg` and `web/thumbs/<name>_1200.jpg` exist (new images; older thumbs may still be `_1024`)
- [ ] Plate solve run on the same pixels as the display copy
- [ ] `label` unique across the manifest, `slug` derived from it
- [ ] `solved: true`
- [ ] Commit and push skydome — check it appears at `tubbers.github.io/gallery/`
- [ ] Add the capture entry to `gallery.json`, commit and push
- [ ] Open the image, hit the Moon button, confirm the scale looks right

That last one is the cheapest end-to-end test there is. If the Moon comes out
obviously wrong, the plate solve doesn't match the published file.
