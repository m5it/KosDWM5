# Plan: Add About Window and HTTP Panel API for Gadgets
## ID: 1784901546.4543912
## Created: 2026-07-24 14:59:06
## Status: completed

### Goal:
Create two new features:

1. **About Window**: Add to the right-side dropdown menu (where gadget/panel configs are) at the bottom. Show KosDWM version, credits, and system info.

2. **HTTP Panel API**: Create a shared HTTP API service in the panel that gadgets can register endpoints with:
   - Panel runs a single HTTP server (e.g., port 8080)
   - Gadgets register their endpoints: `panel.api.register("/notices", handler)`
   - Gadgets can also register multiple endpoints: `/notices/add`, `/notices/delete`, etc.
   - Avoids duplicate servers - each gadget doesn't run its own HTTP server
   - Centralized API management through the panel

Design the API so gadgets can easily expose HTTP endpoints without managing their own servers.

### Tasks (5):
1. [completed] Add an About window to the right-side configuration dropdown
   ID: 1784901551.9890764
   Progress logs: 1 entries

2. [completed] Create a centralized HTTP API service in the panel:
- Panel 
   ID: 1784901558.0810134

3. [completed] Allow gadgets to register HTTP endpoints with the panel:
- G
   ID: 1784901563.0429819

4. [completed] Refactor NoticesGadget to use the shared Panel HTTP API:
- R
   ID: 1784901567.3446538

5. [completed] Test the complete HTTP Panel API:
- Test About window displa
   ID: 1784901572.2596061

---

