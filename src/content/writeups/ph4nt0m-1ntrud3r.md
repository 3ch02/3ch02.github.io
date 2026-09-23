---
# Imported from Obsidian: CTF/picoCTF/Writeup - Ph4nt0m 1ntrud3r.md
# Draft: very short note
title: Ph4nt0m 1ntrud3r
category: Forensics
ctf: picoCTF
date: 2026-08-07
summary: A digital ghost has breached my defenses, and my sensitive data has been stolen! 😱💻 Your mission is to uncover how this phantom intruder infiltrated my system and retrieve the…
tags:
- forensics
- picoctf
lang: fr
draft: true
imported: true
---

Description

A digital ghost has breached my defenses, and my sensitive data has been stolen! 😱💻 Your mission is to uncover how this phantom intruder infiltrated my system and retrieve the hidden flag.

To solve this challenge, you'll need to analyze the provided PCAP file and track down the attack method. The attacker has cleverly concealed his moves in well timely manner. Dive into the network traffic, apply the right filters and show off your forensic prowess and unmask the digital intruder!

Find the PCAP file here [Network Traffic PCAP file](https://challenge-files.picoctf.net/c_verbal_sleep/b6fbb3a5560749f838cdc6db4950985767c4691db3a7b34a220e5654ee39e700/myNetworkTraffic.pcap) and try to get the flag.

```
file myNetworkTraffic.pcap 
```

```
myNetworkTraffic.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Raw IPv4, capture length 65535)

```
