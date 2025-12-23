# TASK-002: Customizable Output Columns + HasAudio

**Created:** 2025-12-22 | **Status:** IMPLEMENTED | **Priority:** High

---

## Summary

Two requests from colleague:
1. Add `HasAudio` column to WORK output (next to Mainline Translation)
2. Allow users to customize which optional columns appear in output

**Scope:** MAIN TAB only (within WORKING processor). Other tabs in WORKING processor not affected.

---

## Column Classification

### MANDATORY Columns (Always Present - Cannot Disable)

These are required for VRS logic to function:

| Column | Purpose |
|--------|---------|
| SequenceName | Row identification key |
| EventName | Row identification key |
| StrOrigin | Row identification key |
| CharacterKey | Character identification |
| CharacterName | Character display name |
| CastingKey | Matching key (auto-generated) |
| DialogVoice | Voice assignment |
| Text | Core content |
| STATUS | Status tracking |
| CHANGES | Change detection result |

### AUTO-GENERATED Columns (VRS Logic Creates These)

User can choose to INCLUDE or EXCLUDE these:

| Column | Description | When Generated |
|--------|-------------|----------------|
| `PreviousData` | Previous Text/Status/Freememo combined | When row matched to previous |
| `PreviousText` | Previous row's Text value | When matched (not New Row) |
| `PreviousEventName` | Previous EventName | Only when EventName changed |
| `DETAILED_CHANGES` | Full composite change type | Always (from detection) |
| `Previous StrOrigin` | Previous row's StrOrigin | When matched |
| `Mainline Translation` | Current Text before import | Always |

### OPTIONAL Columns (From Source Files)

User can choose which to include. Source: CURRENT or PREVIOUS file.

| Column | Default | Source | Notes |
|--------|---------|--------|-------|
| `Desc` | ON | CURRENT/PREVIOUS | Description field |
| `FREEMEMO` | ON | CURRENT/PREVIOUS | Free memo field |
| `SubTimelineName` | ON | CURRENT/PREVIOUS | Timeline info |
| `StartFrame` | ON | CURRENT/PREVIOUS | Frame data |
| `EndFrame` | ON | CURRENT/PREVIOUS | Frame data |
| `DialogType` | ON | CURRENT/PREVIOUS | Dialog classification |
| `Group` | ON | CURRENT/PREVIOUS | Grouping info |
| `UpdateTime` | ON | CURRENT/PREVIOUS | Update timestamp |
| `Tribe` | ON | CURRENT/PREVIOUS | Character attribute |
| `Age` | ON | CURRENT/PREVIOUS | Character attribute |
| `Gender` | ON | CURRENT/PREVIOUS | Character attribute |
| `Job` | ON | CURRENT/PREVIOUS | Character attribute |
| `Region` | ON | CURRENT/PREVIOUS | Character attribute |
| `HasAudio` | ON | CURRENT/PREVIOUS | **NEW - Audio flag** |
| `UseSubtitle` | ON | CURRENT/PREVIOUS | Subtitle flag |
| `Record` | ON | CURRENT/PREVIOUS | Record flag |
| `isNew` | ON | CURRENT/PREVIOUS | New flag |

**All optional columns ON by default. User can choose source: CURRENT or PREVIOUS.**

---

## Settings Schema (JSON)

```json
{
  "use_priority_change": true,
  "output_columns": {
    "auto_generated": {
      "PreviousData": { "enabled": true },
      "PreviousText": { "enabled": true },
      "PreviousEventName": { "enabled": true },
      "DETAILED_CHANGES": { "enabled": true },
      "Previous StrOrigin": { "enabled": true },
      "Mainline Translation": { "enabled": true }
    },
    "optional": {
      "Desc": { "enabled": true, "source": "CURRENT" },
      "FREEMEMO": { "enabled": true, "source": "CURRENT" },
      "SubTimelineName": { "enabled": true, "source": "CURRENT" },
      "StartFrame": { "enabled": true, "source": "CURRENT" },
      "EndFrame": { "enabled": true, "source": "CURRENT" },
      "DialogType": { "enabled": true, "source": "CURRENT" },
      "Group": { "enabled": true, "source": "CURRENT" },
      "UpdateTime": { "enabled": true, "source": "CURRENT" },
      "Tribe": { "enabled": true, "source": "CURRENT" },
      "Age": { "enabled": true, "source": "CURRENT" },
      "Gender": { "enabled": true, "source": "CURRENT" },
      "Job": { "enabled": true, "source": "CURRENT" },
      "Region": { "enabled": true, "source": "CURRENT" },
      "HasAudio": { "enabled": true, "source": "CURRENT" },
      "UseSubtitle": { "enabled": true, "source": "CURRENT" },
      "Record": { "enabled": true, "source": "CURRENT" },
      "isNew": { "enabled": true, "source": "CURRENT" }
    }
  }
}
```

**Source options:** `"CURRENT"` or `"PREVIOUS"`

---

## Implementation Plan

### Phase 1: Add HasAudio (Quick Win)
1. Add `HasAudio` to `OUTPUT_COLUMNS` in `src/config.py`
2. Place after `Mainline Translation`
3. Test with CURRENT file

### Phase 2: Settings Schema
1. Expand `src/settings.py` with column configuration
2. Add default values for all columns
3. Add load/save functions for column settings

### Phase 3: Dynamic Column Filtering
1. Modify `filter_output_columns()` in `src/utils/data_processing.py`
2. Read column settings and filter dynamically
3. Maintain column ORDER (mandatory → auto-generated → optional)

### Phase 4: UI Integration (if GUI exists)
1. Add settings panel for column toggles
2. Group by category (Auto-Generated vs Optional)
3. Add HELP tooltip explaining each auto-generated column

#### UI Mockup (Approved)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Column Settings                                              [X] Close │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─ MANDATORY COLUMNS (Always Shown) ─────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  🔒 SequenceName    🔒 EventName    🔒 StrOrigin    🔒 CharacterKey    │ │
│  │  🔒 CharacterName   🔒 CastingKey   🔒 DialogVoice  🔒 Text            │ │
│  │  🔒 STATUS          🔒 CHANGES                                         │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ AUTO-GENERATED COLUMNS ───────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Column                  Show    Info                                   │ │
│  │  ─────────────────────────────────────────                              │ │
│  │  PreviousData            [✓]     ⓘ Combined prev Text|STATUS|Freememo  │ │
│  │  PreviousText            [✓]     ⓘ Text from matched previous row      │ │
│  │  PreviousEventName       [✓]     ⓘ Previous EventName when changed     │ │
│  │  DETAILED_CHANGES        [✓]     ⓘ Full composite change type          │ │
│  │  Previous StrOrigin      [✓]     ⓘ StrOrigin from previous row         │ │
│  │  Mainline Translation    [✓]     ⓘ Original Text before import         │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─ OPTIONAL COLUMNS ─────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  Column           Show    Source                                        │ │
│  │  ───────────────────────────────────────────                            │ │
│  │  Desc             [✓]     ( ) CURRENT  (•) PREVIOUS                     │ │
│  │  FREEMEMO         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  SubTimelineName  [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  StartFrame       [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  EndFrame         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  DialogType       [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Group            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  UpdateTime       [ ]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Tribe            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Age              [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Gender           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Job              [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Region           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  HasAudio         [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  UseSubtitle      [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  Record           [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │  isNew            [✓]     (•) CURRENT  ( ) PREVIOUS                     │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  [Reset to Defaults]                      [Cancel]  [Apply & Save]  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Access:** Button in MAIN TAB toolbar: `[⚙️ Columns]`

### Phase 5: Help System
One-liner explanations for auto-generated columns:

| Column | Help Text |
|--------|-----------|
| PreviousData | "Combined previous Text, STATUS, FREEMEMO (format: Text \| STATUS \| Freememo)" |
| PreviousText | "Text value from matched previous row" |
| PreviousEventName | "Previous EventName when it changed" |
| DETAILED_CHANGES | "Full composite change type (all detected changes)" |
| Previous StrOrigin | "StrOrigin value from matched previous row" |
| Mainline Translation | "Original Text value before import logic applied" |

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/config.py` | Add HasAudio to OUTPUT_COLUMNS |
| `src/settings.py` | Expand with column settings schema |
| `src/utils/data_processing.py` | Dynamic column filtering |
| GUI file (TBD) | Settings panel |

---

## Decisions Confirmed (2025-12-22)

1. **Column source**: User CAN choose CURRENT vs PREVIOUS for each optional column
2. **HasAudio placement**: After Mainline Translation - CONFIRMED
3. **Defaults**: All optional columns ON by default, user deactivates if needed

---

## Testing

- [ ] HasAudio appears in output
- [ ] Settings persist between sessions
- [ ] Disabling column removes it from output
- [ ] Mandatory columns cannot be disabled
- [ ] Column order is maintained

---

*Task created from colleague request - see SESSION_CONTEXT for conversation*
