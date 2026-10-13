---
title: "VoIP network with FreePBX / Asterisk"
summary: "A company telephony lab: FreePBX and Asterisk behind a pfSense firewall, softphone clients, voicemail and French prompts, plus a deployment manual that also covers encrypting calls with TLS and SRTP."
status: completed
date: 2025-08-12   # date of the deployment manual — used for sorting only, not displayed
order: 4
tags:
  - network
  - lab
  - voip
  - telephony
stack:
  - FreePBX
  - Asterisk
  - pfSense
  - SIP / RTP
  - TLS / SRTP
  - Zoiper
  - VMware
---

## Context

A personal project: build the internal telephony of a small company on an IP network instead of traditional phone lines, and write the whole thing down as a deployment manual that someone else could follow.

The project uses an on-premises IP PBX (FreePBX, the web interface for Asterisk) rather than a hosted one, so every component is installed and configured by hand.

## How it was organised

1. **Fundamentals** — what happens during a call: SIP for signalling (port 5060), RTP for the audio, codecs, the dial plan, and the supporting protocols (DHCP, DNS, NTP, and STUN/TURN/ICE when NAT is involved).
2. **Architecture** — a pfSense firewall providing the LAN, DHCP and Internet access; a FreePBX server on that LAN; Windows clients running the Zoiper softphone.
3. **Deployment manual** — every step from creating the virtual machines to placing the first call.

## What I did

- Installed **pfSense** with a WAN and a LAN interface and a DHCP scope for the LAN.
- Installed the **FreePBX** distribution, completed the first-run setup (administrator account, update schedule, built-in firewall) and placed the server on the pfSense LAN.
- Created **PJSIP extensions** for each user, with a secret, a caller ID and optional voicemail.
- Registered **Zoiper** softphones on the client machines and placed calls between extensions.
- Configured **voicemail** per extension, the ring time before a call goes to voicemail, and the feature codes used to listen to messages.
- Installed the **French sound prompts** with `fwconsole` and set French as the default language, system-wide or per extension.

## Securing the calls

By default, SIP and RTP are not encrypted: anyone on the path can read the signalling and listen to the audio. The manual covers:

- **Strong, random secrets** for every extension.
- **TLS for the signalling** (SIP over TLS, port 5061) with a certificate managed in FreePBX.
- **SRTP for the audio**, enabled per extension, with TLS as the only allowed transport.
- **Fail2ban**, built into FreePBX, to ban addresses after repeated failed registrations.

## What I learned

- A phone call is two separate flows — signalling and media — and each one has to be secured on its own.
- The softphones have to sit on the same network as the PBX to register: telephony problems are often network problems first.
- Most of the security features are available but switched off by default — encryption has to be enabled explicitly, extension by extension.

## Not done yet

The SIP trunk between two sites (calls between two companies on different networks) is planned in the manual but not documented yet.
