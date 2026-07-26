# Plan: Fix DateTime Settings in Panel
## ID: 1784980704.9931352
## Created: 2026-07-25 12:58:24
## Status: completed

### Goal:
The Panel class needs to load datetime configuration from panel.json and apply it when updating the time label. Currently, update_time() hardcodes "%H:%M" and ignores all settings like show_date, date_format, time_format, etc.

### Tasks (4):
1. [completed] Add "xdgmenumaker" as a new option in the Type dropdown (QCo
   ID: 1784980707.912922
   Progress logs: 2 entries

2. [pending] Load datetime config in Panel.__init__
   ID: 1785084320.3720214

3. [pending] Rewrite update_time() to use datetime config
   ID: 1785084324.1829045

4. [pending] Add datetime config reload mechanism
   ID: 1785084328.1785846

---

