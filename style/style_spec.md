# Read-Only: style spec (Act 1)

M4's first step. Act 1 (S01a–S40) is stylized Blender with CC0 textures (brief, "Overview"). Act 2 (S41 on) is the
same cameras and set made photoreal at M5. So Act 1 must read as made: clean shapes, real grime in the surfaces,
and theatrical light. The video's reveal is the switch from this look to photoreal. `config/look.json` holds every
number here; change this file first, then the config.

**Sources.**
- **The brief:** grime in the architecture, not the people; no Reddit logos or UI; the Tenderloin-edge composite; the
  eatery as a fictional r/Philippines.
- **The human's notes:** the eatery is "*extremely* informal, a hole-in-the-wall ... a turo-turo ... clean as one
  might expect of the area ... very much not polished" (`reference/README.md`).
- **The style prompt:** late-'90s boom-bap.
- **There are no reference videos.**

## The look in one line

A sodium-orange street at night under a cold glass tower: warm, worn, hand-lettered shops below; one clean, blue-white
corporate light above. Red is reserved for what records and what closes: the REC lights and the READ-ONLY neon.

## Format and motion

- 24 fps (brief), 1920×1080 final; drafts at 1280×720 (`config/render_profiles.json`).
- Eevee motion blur, shutter 0.5. Boom-bap is about weight on the beat, so moves land on beats and hold. Nothing
  floats.
- AgX, "Medium High Contrast" look, exposure -0.3: deep, inky shadows with readable mid-tones.

## Palette (`config/look.json` → `palette`)

| Role | Key | Hex | Where |
| --- | --- | --- | --- |
| Street light | `sodium` | `#ffad5a` | the street lamps (low-pressure-sodium orange: the old Tenderloin night) |
| Night | `night` | `#1b2740` | sky, moon fill, every shadow (shadows stay blue, never grey) |
| The tower | `corporate` | `#cfe6ff` | the tower's glass, lobby and billboard: clean, cold, white-blue |
| Recording and closing | `rec` | `#ff2a2a` | REC lights, READ-ONLY neon, the BLACKMAIL screen. Nothing else is red. |
| The community | `community` | `#ffd38a` | lit shop interiors, upper windows, lanterns: the warm life of the block |
| The eatery | `turo` | `#ffe6b0` | the eatery's fluorescent-warm interior; its yellow walls and green trays |
| Money | `gold` | `#e2b63b` | VIP badges, the bell, padlocks, briefcases |
| The mods | `vest` | `#ff7a1a` | the mods' vests |
| The ticker and the screens | `screen` | `#7fe0ff`, ticker `#55ff7a` | the tower's displays |

- **Red against orange.** Sodium (hue 31°) and the REC red (hue 0°) must never blur together. The neon is
  saturated and emissive, and the lamps are a broad wash, so they read apart. Check S14 and S48.
- **No Reddit orange-red** (#ff4500) anywhere. It would read as a logo colour.

## Materials

| Surface | Texture (CC0, `assets/textures/`) | Treatment |
| --- | --- | --- |
| Street | `asphalt_03` | darkened, slightly wet (roughness 0.55) so the lamps pool in it |
| Sidewalks | `concrete_pavement` | 1.5 m squares, as the grey-box |
| Facades | `brick_4`, `concrete_wall_003`, `blue_plaster_weathered` | one per shop in turn; stains kept |
| Shutters | `painted_metal_shutter` | grey-green paint; tag graffiti on some (decals) |
| Boarded windows | `plywood` | FOR LEASE, and the scaffold's boards |
| Park | `grass_ground` | patchy |
| Plots, paths | `dry_ground_01` | |
| Headstones, payphone post | `concrete` | |
| Eatery floor | `brown_floor_tiles` | the reference photos' terracotta tile |
| The Dev's shop floor | `old_linoleum_flooring_01` | |
| Tower | none | flat glass and brushed metal: the only clean surface on the street |

Textures are box-projected in object space at their real-world scale (a brick is a brick at every shop), so no
mesh needs UVs.

## Lettering

- **Shop signs:** plain painted lettering (Inter, OFL), dark on cream, as the grey-box. They are never Reddit's fonts
  or logo. The eatery's sign is "hand-painted": a warmer cream ground, with slight unevenness at M4 polish.
- **The tower:** the same Inter, white on glass. It's clean on purpose.
- **Graffiti:** shapes and tags made up for this video: no real tags, no words.

## Characters (stylized figures)

Toy-like and readable: rounded capsule bodies, oversized heads, simple faces (two dot eyes, a mouth shape driven
by the vocal stem). No likenesses. Each is defined by silhouette and colour:

| Character | Silhouette | Colours |
| --- | --- | --- |
| The Dev | hoodie with the hood down, shop apron, tool belt | teal hoodie, tan apron |
| The CEO | hoodie under an ermine cape, crown-like collar | grey hoodie, white cape with black ermine spots, red lining |
| The mods | MOD vests, brooms | blue-grey, safety orange |
| The VIP bots | tall, square-shouldered, suited robots with briefcases | gunmetal suits, gold VIP badges, cyan eye slits |
| The good bots | small, round, homemade (visible screws, mismatched parts) | cream and pale blue, with warm lanterns |
| The hype man | a pure black silhouette in a lit doorway | |

Mouths: Rhubarb Lip Sync on the lead stem picks mouth shapes for the B+M shots, with the lyrics as the dialog text.
The grey-box loudness drive stays as a fallback.

## Light

- **Night key:** the sodium lamps (spots, soft shadows), with a cool moon fill from the north-west at a fraction of
  their strength.
- **The tower:** lights itself and spills cold light across the north sidewalk.
- **Shop interiors:** warm, until the shutters close.
- **The eatery:** warm and busy by day in the pre-roll; a soft morning sun from the east.
- **A light haze** (world volume, very low density) so the lamp cones and the neon read in the air.
