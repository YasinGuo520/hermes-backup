---
name: apple-calendar
description: "macOS Calendar automation via AppleScript — read, create, copy, delete events and alarms."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Calendar, macOS, Apple, AppleScript, iCloud]
    category: apple
prerequisites: []
---

# Apple Calendar (macOS)

Manage macOS Calendar (iCal) events via AppleScript (`osascript -e`). All changes sync to iCloud and push notifications to the user's iOS devices when alarms are set.

## When to Use

- User asks to read, create, copy, or delete calendar events
- User wants to copy yesterday's schedule to today
- User wants alarms/reminders on calendar events
- User wants a daily schedule overview
- Tasks that would sync to the user's iPhone Calendar

## When NOT to Use

- **Reminders/tasks** → use `apple-reminders` skill (remindctl) instead
- **Scheduling agent alerts** → use the `cronjob` tool
- **Google Calendar / Feishu Calendar** → use their respective APIs or skills
- Short one-off events the user wants a phone notification for → prefer `apple-reminders` (Reminders push more reliably)

## Preferred Workflow

**Do NOT use `computer_use` GUI approach for Calendar.** The Calendar accessibility tree is unreliable (often returns 0×0 screenshots, 1974+ elements with no window geometry, invisible windows). AppleScript is the correct interface.

All operations go through `osascript -e 'tell application "Calendar" ... end tell'`.

## Quick Reference

### Get Today's Date Set to Midnight

```applescript
set todayDate to current date
set day of todayDate to 7           -- adjust
set month of todayDate to 7         -- adjust
set year of todayDate to 2026       -- adjust
set time of todayDate to 0          -- midnight
```

**Important:** Set `time of todayDate` AFTER setting day/month/year. Setting `time` before date fields can corrupt the time.

Better approach — use offset arithmetic to avoid date-field ordering bugs:

```applescript
set todayDate to current date
set day of todayDate to 7
set month of todayDate to 7
set year of todayDate to 2026
set time of todayDate to 0
set tomorrowDate to todayDate + (1 * days)

-- Then create event times by adding hours:
set evStart to todayDate + (9 * hours)       -- 9:00 AM
set evEnd to todayDate + (12 * hours)        -- 12:00 PM
```

### List Calendars

```bash
osascript -e 'tell application "Calendar" to set calNames to title of every calendar'
```

### Get a Specific Calendar by Name

```applescript
tell application "Calendar"
    set cal to calendar "个人"  -- "Personal" in Chinese locale; use localized name
end tell
```

Common localized names:
- English: "Home", "Work", "Personal"
- Chinese: "个人", "工作"

Use `title of every calendar` to discover the user's calendar names first.

### Read Events for a Date Range

```applescript
tell application "Calendar"
    set cal to calendar "个人"
    set evts to (every event of cal whose start date ≥ todayDate and start date < tomorrowDate)
    repeat with ev in evts
        set sDate to start date of ev
        set eDate to end date of ev
        set sTxt to time string of sDate
        set eTxt to time string of eDate
        log sTxt & " - " & eTxt & "  " & summary of ev
    end repeat
end tell
```

### Create Events with Alarms

```applescript
tell application "Calendar"
    set cal to calendar "个人"
    set evStart to todayDate + (9 * hours)
    set evEnd to todayDate + (10 * hours)
    set newEvent to make new event at end of events of cal with properties {¬
        summary:"📖 Meeting", start date:evStart, end date:evEnd}
    make new display alarm at end of display alarms of newEvent with ¬
        properties {trigger interval:-5}  -- 5 minutes before
end tell
```

`trigger interval` is in seconds, negative means "before". So:
- `-5` = 5 seconds before ❌
- `-300` = 5 minutes before ✅
- `-600` = 10 minutes before
- `-3600` = 1 hour before

**Correct:** `-300` for 5 minutes, `-900` for 15 minutes — AppleScript `minutes` keyword works too: `trigger interval:-5 * minutes`

### Delete All Events for a Day

```applescript
tell application "Calendar"
    set cal to calendar "个人"
    set evts to (every event of cal whose start date ≥ todayDate and start date < tomorrowDate)
    repeat with ev in evts
        delete ev
    end repeat
end tell
```

## Pitfalls

1. **`time of date` ordering bug:** Setting `time of evStart to 9 * hours` AFTER setting day/month/year resets the time. Always set `time of` FIRST on the ref date, then use `+ (N * hours)` offset arithmetic for each event.

2. **Reading alarms back is unreliable:** `alarms of ev` throws a type conversion error (-1700) in many macOS versions. Don't rely on reading alarms to verify they were created. Instead, verify by creating a fresh event with the alarm and checking the event count.

3. **`hours of sDate` returns wrong values:** The `hours` property of an AppleScript date can return unexpected values in certain calendar contexts (especially across midnight). Use `time string of sDate` for display, not `hours of sDate`.

4. **Calendar app may have no on-screen window:** Even when running (`Calendar` shows in `list_apps`), the window may be on a different Space or minimized. `computer_use` cannot capture it. Always fall back to AppleScript.

5. **Localized calendar names:** Default calendar name varies by system language. On Chinese macOS it's "个人" (Personal), on English it's "Home" or "Personal". Always call `title of every calendar` to discover names.

6. **`make new display alarm` requires `display alarms of` collection:** Use `make new display alarm at end of display alarms of newEvent`, NOT `make new alarm at end of alarms of newEvent`. The `display alarm` vs `alarm` distinction matters.

7. **Hour arithmetic uses AppleScript units:** `8 * hours` means `8 * 3600 = 28800 seconds` from midnight. Works correctly with date+offset arithmetic.
