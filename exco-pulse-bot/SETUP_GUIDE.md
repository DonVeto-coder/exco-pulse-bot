# OEB Exco Pulse — full-dashboard image, fully automated

This bot renders the **complete** Exco Action Tracker dashboard (waffle, owner bars,
delivery-pulse sparklines, figures) to a PNG every Monday and drops it into the same
SharePoint folder your existing flow already uses. Your **Power Automate flow stays as
it is** and simply attaches that image instead of the simple tiles.

```
Mon 07:30 SAST  GitHub Actions  → read workbook → render full PNG → save pulse.png to SharePoint
Mon 08:00 SAST  Power Automate  → attach pulse.png → send to Exco (unchanged)
```

Everything runs in the cloud. No PC. Once set up, it is hands-off.

---

## Part 1 — The credential (one-time, IT / admin)

The bot needs permission to **read the workbook and write `pulse.png`** into the OEB EXCO
site. It does **not** need send-mail — your flow already sends.

In the Microsoft **Entra admin center → App registrations → New registration**:

1. Name: `OEB Exco Pulse Bot`. Register.
2. **API permissions → Add → Microsoft Graph → Application permissions**:
   - `Sites.Selected`  *(recommended, least privilege)* — or `Sites.ReadWrite.All` if you prefer simpler.
3. **Grant admin consent**.
4. If you chose `Sites.Selected`, grant this app **read/write to the one site only**
   (`https://oebearings.sharepoint.com/sites/OEBEXCO`). An admin does this once with a
   Graph call (`PUT /sites/{siteId}/permissions`, roles: `["write"]`) — happy to supply the exact command.
5. **Certificates & secrets → New client secret** (24-month). Copy the **Value** now.
6. From **Overview**, copy the **Directory (tenant) ID** and **Application (client) ID**.

You now have three values: **TENANT_ID**, **CLIENT_ID**, **CLIENT_SECRET**.
The fourth, **DRIVE_ID**, is already known:

```
b!af9HXC_f5ku1a9ZGaYXQnp2d3uRMUqZAob7gaJogeGtbwEncpnwPTJup4l4RqpOE
```

---

## Part 2 — The GitHub repo (one-time)

1. Create a **private** GitHub repo (e.g. `exco-pulse-bot`).
2. Upload everything in this folder (or `git push` it).
3. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, add four:
   - `TENANT_ID`
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - `DRIVE_ID`  (the value above)
4. **Actions tab → "OEB Exco Pulse" → Run workflow** (manual run).
   - It should finish green and (a) attach a `pulse-png` artifact you can open, and
     (b) place `pulse.png` in `Documents/Action Tracker - Exco/Executive Action Tracker/`.

The weekly schedule (`Mondays 05:30 UTC = 07:30 SAST`) is already set; the manual run is just to test.

---

## Part 3 — One small edit to your Power Automate flow

Your flow currently attaches the Office Script's output. Point it at the file instead:

1. Edit the flow. **Add an action** *before* "Send an email (V2)":
   **SharePoint → Get file content using path**
   - Site Address: `OEB EXCO`
   - File Path: `/Documents/Action Tracker - Exco/Executive Action Tracker/pulse.png`
2. In **Send an email (V2) → Attachments → Content - 1**: replace the current
   `body/result/...` value with the **File Content** from the step you just added.
   Leave **Name - 1** as `pulse.png`.
3. (Optional) Delete the **Run script** step — it is no longer needed.
4. **Save.** Run the flow once to confirm the full dashboard now arrives.

> Timing: the GitHub job runs at 07:30 SAST so the image is ready well before the 08:00 send.
> If you ever change either time, keep the render at least ~15 min before the send.

---

## Before it goes live to Exco — two charts to finalise

The render is live for the date, the waffle, the owner bars, and all nine delivery-pulse
sparklines (verified against the original). **Two company-level charts still show reference
numbers** and should be finalised first:

- the **heartbeat strip** at the very top (company-wide pulse) — quick to make live;
- the **past-performance "week-on-week commitments"** bars at the bottom — these need
  confirmation of how the weekly commitment totals are defined (Tim's input).

Until those are confirmed, treat the bottom two charts as illustrative.

---

## Files in this package

| File | Purpose |
|---|---|
| `run.py` | Orchestrates: download workbook → build HTML → render → upload PNG |
| `graph.py` | Microsoft Graph client (download / upload) |
| `gen_data.py` | Reads the workbook, computes every dashboard figure |
| `build_html.py` | Injects live data into the dashboard template |
| `spark.py` | Draws the delivery-pulse sparklines (SVG) |
| `template.html` | The OEB dashboard layout (the design) |
| `render.js` | Headless-browser render to PNG (734px, 2× scale) |
| `.github/workflows/exco-pulse.yml` | The weekly schedule + steps |
