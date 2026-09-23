---
# Copy to src/content/ctf/<slug>.md — URL: /ctf/<slug>/
name: "Competition name 2026"
year: 2026
# date: 2026-MM-DD         # optional — leave out rather than guess
handle: "3ch0"             # handle you played under (optional)
team: "team_name"
# role: "Team captain"     # optional
# format: "Jeopardy, 48h"  # optional
# organizer: "..."         # optional
# url: https://...         # optional
categories:
  - Web
  - Forensics
# Ordered stages. The last *completed* stage with a rank is shown as the result.
# Stages that are not completed are always displayed as pending ("Final — Upcoming"),
# so a qualification result is never presented as a final result.
stages:
  - name: "Final ranking"
    status: completed      # completed | ongoing | upcoming
    rank: 3
    # outOf: 40            # optional: number of teams
# cover: ./images/my-photo.jpg   # optional: shown on the Achievements card before clicking through.
                                  # Put the image next to this file (e.g. src/content/ctf/images/),
                                  # any format (jpg/png/webp…) — Astro optimises it automatically.
---

A few lines about the competition: format, what you worked on, what you learned.
