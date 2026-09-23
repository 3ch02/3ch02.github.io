---
title: "Sankofa Cyber"
summary: "A platform for security awareness and human risk management: realistic social-engineering simulations (phishing, smishing, quishing, vishing), hands-on labs, and a per-user Human Risk Score to measure and reduce exposure."
status: in-progress
date: 2026-06-01   # approximate start (repository history) — used for sorting only, not displayed
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
---

## The problem

Firewalls, EDR and XDR keep improving, but most successful intrusions still start with a person: a convincing email, a QR code on a poster, an SMS about a parcel, a phone call that sounds like the boss. Generative AI makes those lures cheaper and more convincing.

Most awareness programs answer this with theoretical quizzes or one generic phishing simulation per year. They rarely tell an organisation **how exposed it actually is**, or **who needs what training**.

## The idea: train → test → measure → fix

Sankofa Cyber is built around a continuous loop:

1. **Train** — short, practical modules and labs.
2. **Test** — realistic, multi-channel social-engineering simulations.
3. **Measure** — translate observed behaviour into a **Human Risk Score (HRS)**.
4. **Fix** — assign targeted remediation based on what actually went wrong.

## Threats covered

| Vector | What is simulated |
| --- | --- |
| Phishing / spear-phishing | Contextual emails imitating colleagues, partners or internal services |
| Smishing | SMS lures targeting the personal / professional overlap (BYOD) |
| Quishing | Malicious QR codes that bypass classic mail filters |
| Vishing | Voice messages using a *generic* executive-style synthetic voice — never a cloned real person |
| Social engineering | Fake calendar invites, malicious-looking attachments, pretexting scenarios |

## Two spaces

- **Sankofa Academy** — a learning space for students and individuals: awareness paths, and labs where you analyse email headers, inspect suspicious URLs or spot anomalies on a fake login page.
- **Sankofa Enterprise** — a console for security teams: employee segmentation by department, a multi-channel campaign orchestrator, and a dashboard of the organisation's human risk posture.

## Measuring human risk

Each user gets a score from 0 to 100 built from four weighted dimensions:

| Dimension | Weight | Based on |
| --- | --- | --- |
| Vigilance | 0.25 | Reporting rate, time to report, accuracy of reports |
| Resistance | 0.35 | Behaviour during simulations: no click, hover then click, click, credentials submitted |
| Competence | 0.25 | Results in hands-on labs |
| Hygiene | 0.15 | Optional external signals (e.g. breached passwords), with consent |

A contextual coefficient (department exposure, seniority) adjusts the score, but it is **capped at 1.5** so that context alone can never push someone into the "critical" band — behaviour has to.

## Privacy by design

A platform that simulates attacks on people has to be careful with their data:

- Fake login pages record **that** something was submitted, **never what** was typed.
- Only anonymised, generic prompts are sent to the external AI model; names, infrastructure details and scores stay in the application database.
- Role-based access control and strict tenant isolation between organisations.

## Stack

Next.js 15 (App Router, Server Actions) and TypeScript, Tailwind CSS, Prisma with SQLite in development and PostgreSQL targeted for production, Auth.js for sessions and roles, and the Gemini API for scenario generation and learner feedback.

## Status & roadmap

The project is **in active development**. The roadmap goes from the core email phishing engine and HRS calculation, to additional channels (quishing, smishing, voice), a report-phishing add-in, an AI debrief assistant, and later a browser agent and a Human Risk API that other security tools could query.
