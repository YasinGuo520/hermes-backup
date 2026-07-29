# macOS Calendar via AppleScript

Create, update, and delete macOS Calendar events programmatically using `osascript`.

## Create a Single Event

```bash
osascript -e 'tell application "Calendar" to tell calendar "个人" to make new event with properties {summary:"事件标题", start date:date "2026-07-06 09:00:00", end date:date "2026-07-06 10:00:00", description:"备注说明"}'
```

**Calendar names** (macOS Chinese locale):
| Name | Type | Sync |
|------|------|------|
| `日历` | Local | ❌ No iCloud |
| `个人` | iCloud | ✅ iCloud → iPhone |
| `工作` | iCloud | ✅ iCloud → iPhone |

## Create Multiple Events (sequential calls)

AppleScript returns after the first `make new event`, so batch calls must be in separate `osascript` invocations:

```bash
osascript -e 'tell application "Calendar" to tell calendar "个人" to make new event with properties {summary:"事件1", start date:date "2026-07-06 08:00:00", end date:date "2026-07-06 09:00:00"}'
osascript -e 'tell application "Calendar" to tell calendar "个人" to make new event with properties {summary:"事件2", start date:date "2026-07-06 09:00:00", end date:date "2026-07-06 12:00:00"}'
```

## Delete Events

```bash
# Delete all events on a specific date in a specific calendar
osascript -e '
tell application "Calendar"
    delete every event of calendar "个人" whose start date ≥ date "2026-07-06 00:00:00" and start date ≤ date "2026-07-06 23:59:00"
end tell'
```

## List Available Calendars

```bash
osascript -e 'tell application "Calendar" to get name of every calendar'
```

## Pitfalls

- `start date` and `end date` use `date "YYYY-MM-DD HH:MM:SS"` format
- End date on a future day: `date "2026-07-07 00:00:00"`
- To sync to iPhone: create events in an iCloud-synced calendar (`个人` or `工作`), NOT in `日历`
- Disable Mac notifications: System Settings → Notifications → Calendar → OFF
- Keep iPhone notifications: Settings → Notifications → Calendar → ON
