---
title: "Sankofa Cyber"
summary: "A platform for security awareness and human risk management: realistic multi-channel social-engineering simulations, hands-on labs, and a per-user Human Risk Score to measure and reduce exposure."
status: in-progress
date: 2026-08-08   # repository start — used for sorting only, not displayed
featured: true
order: 1
tags:
  - awareness
  - phishing
  - social-engineering
  - human-risk
stack:
  - Next.js 15
  - TypeScript
  - Tailwind CSS
  - Prisma
  - PostgreSQL
  - Auth.js
  - Gemini API
demo: https://cyber-sankofa.vercel.app/
---

## The problem

Firewalls, EDR and XDR keep improving, but most successful intrusions still start with a person: a convincing email, a QR code on a poster, an SMS about a parcel, a phone call that sounds like the boss. Generative AI makes those lures cheaper and more convincing.

Most awareness programs answer this with theoretical quizzes or one generic phishing simulation per year. They rarely tell an organisation **how exposed it actually is**, or **who needs what training**.

## The idea: train → test → measure → fix

Sankofa Cyber is built around a continuous loop:

1. **Train** — short, practical modules and hands-on labs.
2. **Test** — realistic, multi-channel social-engineering simulations.
3. **Measure** — translate observed behaviour into a **Human Risk Score (HRS)**.
4. **Fix** — assign targeted remediation based on what actually went wrong.

## Threats covered

| Vector | What is simulated |
| --- | --- |
| Phishing / spear-phishing | Contextual emails imitating colleagues, partners or internal services |
| Smishing | SMS lures targeting the personal / professional overlap (BYOD) |
| Quishing | QR-code posters generated per campaign, tracked on scan |
| Vishing | AI-generated voice calls using a *generic* executive-style synthetic voice — never a cloned real person |
| Social engineering | Fake landing pages, pretexting scenarios |

## Two spaces

- **Sankofa Academy** — a learning space for students and individuals: modules, quizzes, badges, a leaderboard, and hands-on labs (auto-graded) where you analyse email headers, inspect suspicious URLs or spot anomalies on a fake login page.
- **Sankofa Enterprise** — a console for security teams: employee and department management, a multi-channel campaign builder, deliverability tracking, and a dashboard of the organisation's human risk posture.

## What's actually built

This isn't a mockup — the [live demo](https://cyber-sankofa.vercel.app/) runs a real Next.js app with authentication (email verification, 2FA, password reset), a Postgres database, and an admin panel behind it. Concretely, today:

- **Academy**: modules and lessons, auto-graded labs, quizzes, certifications, a leaderboard and badges.
- **Enterprise console**: campaign builder across email / SMS / QR / voice, department & employee management, deliverability and report dashboards.
- **Tracking**: an open-tracking pixel, redirect links, landing-page submission events, and a voice call pipeline (gather → status → debrief) — all logged as events, never storing what a user actually typed.
- **Sankofa Shield**: a `/shield/check` API plus an analyze → debrief flow, and an early Gmail add-on for one-click phish reporting.
- **Human Risk Score**: a weighted calculator (with its own unit tests) turning simulation and lab behaviour into the 0–100 score below, plus a small **Human Risk API** (`/api/v1/risk`) other tools could query.
- **AI**: Gemini-backed campaign advice for admins and post-lab debriefs; synthetic voice generation for the vishing channel.

What's *not* there yet: this is still a student project mid-build, not a hardened production system — expect rough edges, incomplete admin flows, and features still being tuned rather than a polished, audited platform.

## Measuring human risk

Each user gets a score from 0 to 100 built from four weighted dimensions:

| Dimension | Weight | Based on |
| --- | --- | --- |
| Vigilance | 0.25 | Reporting rate, time to report, accuracy of reports |
| Resistance | 0.35 | Behaviour during simulations: no click, hover then click, click, credentials submitted |
| Competence | 0.25 | Results in hands-on labs |
| Hygiene | 0.15 | Optional external signals (e.g. breached passwords via HIBP), with consent |

A contextual coefficient (department exposure, seniority) adjusts the score, but it is **capped at 1.5** so that context alone can never push someone into the "critical" band — behaviour has to.

## Privacy by design

A platform that simulates attacks on people has to be careful with their data:

- Fake login pages record **that** something was submitted, **never what** was typed.
- Only anonymised, generic prompts are sent to the external AI model; names, infrastructure details and scores stay in the application database.
- Role-based access control and tenant isolation between organisations.

## Stack

Next.js 15 (App Router, Server Actions) and TypeScript, Tailwind CSS, Prisma over PostgreSQL, Auth.js for sessions and roles, and the Gemini API for scenario generation, campaign advice and debriefs.
