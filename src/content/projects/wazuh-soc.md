---
title: "Log analysis and intrusion detection with Wazuh (SOC lab)"
summary: "Second-year team project: a small SOC built around Wazuh behind a pfSense firewall, with Windows and Linux agents, then eight attack scenarios run from Kali to check what the SIEM actually detects."
status: completed
date: 2026-06-03   # date of the last recorded tests — used for sorting only, not displayed
order: 2
tags:
  - siem
  - soc
  - blue-team
  - detection
  - lab
stack:
  - Wazuh
  - pfSense
  - Syslog
  - Windows 10
  - Ubuntu
  - Kali Linux
  - Hydra
  - Metasploit (msfvenom)
  - Postfix
  - VMware
---

## Context

My second-year school project (PPE), done in a team of three: build an infrastructure that centralises logs and detects intrusions, then prove that it works by attacking it.

Wazuh was chosen as the main platform because it combines a SIEM, host-based detection, file integrity monitoring, vulnerability detection and active response in one open-source tool. ELK and Splunk were studied for comparison.

## Architecture

| Component | Role |
| --- | --- |
| pfSense | Router and firewall (WAN, LAN and DMZ interfaces), DHCP for the LAN, sends its logs to the SIEM |
| Wazuh server | Manager, indexer and dashboard on one virtual machine |
| Windows 10 agent | Monitored workstation |
| Ubuntu agent | Monitored Linux machine |
| Kali Linux | Attacker |

Log flow: the agents report to the Wazuh manager, pfSense forwards its firewall and system events by remote syslog (UDP 514), and everything is indexed and searched from the dashboard.

## What we deployed

- **pfSense** with its interfaces and DHCP.
- The **Wazuh server**, imported from the official virtual appliance, and **agents** installed on the Windows and Ubuntu machines.
- **pfSense → Wazuh integration** by remote syslog: remote logging enabled on the firewall, a syslog listener declared in the manager's `ossec.conf`, and reception checked with `tcpdump`.
- **Real-time file integrity monitoring** on the Windows agent — by default the scan is periodic, so `realtime="yes"` was added on the watched directory.
- **Email alerts**: Postfix on the Wazuh server relaying through an external SMTP service, and notifications enabled in the manager above a severity threshold.

## Detection tests

Each test was run from the attacker machine, then analysed in the dashboard's Discover view.

| # | Scenario | How | What Wazuh reported |
| --- | --- | --- | --- |
| 1 | Connectivity | Agents enrolled and checked in the agent summary | Both agents active |
| 2 | RDP brute force on Windows | `hydra` with a wordlist | Rule 60122 (logon failure), 22 failures correlated from the attacker |
| 3 | SSH brute force on Ubuntu | `hydra` with a wordlist | Rules 5710 / 5712, attacker identified as the source |
| 4 | Vulnerability detection | Vulnerability Detector module on the Windows agent | CVE-2025-21382 (CVSS 7.8, high), shown as solved after the system update |
| 5 | Malware on Linux | Meterpreter payload built with `msfvenom`, downloaded on Ubuntu | Rule 510, flagged as soon as the file was written |
| 6 | File integrity on Windows | A line added to the `hosts` file | Rule 550, level 7: checksum and size changed, mapped to MITRE T1565.001 |
| 7 | Persistence on Windows | Payload fetched with `certutil`, registered as a service with `sc create` | Rule 61138 (new Windows service), mapped to MITRE T1543.003 |
| 8 | Email alerting | Postfix relay and manager notifications | Alert emails delivered |

All eight planned demonstrations were validated.

## What I learned

- **A SIEM only sees what it is fed.** Agent enrolment, the syslog listener and a check of the traffic on the wire all come before the dashboard can be trusted.
- **Defaults matter.** File integrity monitoring is periodic unless real-time mode is switched on, and email notifications only fire above a configured level — a level-7 alert such as the `hosts` modification is recorded but nobody is emailed.
- **One failed logon is noise; correlation makes it an attack.** The brute-force detections come from repetition from a single source, not from any individual event.
- **Playing the attacker makes the alerts readable.** Running an attack and reading the resulting alert side by side shows what each field means and which MITRE ATT&CK technique it maps to.

## Limits

This is a lab on virtual machines, with one firewall and two monitored hosts, and attacks we launched ourselves. Active response (automatically isolating a file or blocking an address) was identified as the next step but not implemented.
