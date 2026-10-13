---
title: "Secure, highly available network with FortiGate (SD-WAN & VPN)"
summary: "A two-site lab on FortiGate VMs: dual-ISP SD-WAN with failover and load balancing, a redundant IPsec site-to-site VPN running over SD-WAN, and remote access for roaming users with FortiClient."
status: completed
date: 2026-04-18   # last lab session — used for sorting only, not displayed
order: 2
tags:
  - network
  - lab
  - vpn
  - sd-wan
  - high-availability
stack:
  - FortiGate (VM)
  - FortiOS
  - SD-WAN
  - IPsec / IKEv2
  - FortiClient
  - VMware
---

## Context

A lab scenario: a company wants to modernise the link between its head office and a branch, and give remote staff secure access. The head office has two Internet providers, and the link has to survive the loss of either one.

Three goals:

1. **WAN redundancy** — SD-WAN on the head-office firewall, with failover and load balancing (ECMP) across the two ISPs.
2. **Site-to-site confidentiality** — an IPsec VPN between the two sites that keeps working when one ISP goes down.
3. **Secure mobility** — a remote-access VPN for roaming users.

## Topology

![Lab topology: head office with two ISPs, branch office, site-to-site IPsec VPN and a remote user on FortiClient](./images/sdwan-vpn-topology.png)

| Site | LAN | WAN |
| --- | --- | --- |
| Head office | `10.0.0.0/24` | WAN1 `192.168.56.10`, WAN2 `192.168.56.20` |
| Branch | `10.1.0.0/24` | `192.168.56.30` |
| Remote users | pool `10.212.134.100–200` | FortiClient |

Everything runs on two FortiGate VMs, with one virtual network standing in for the Internet and one per LAN.

## What I did

### SD-WAN on the head office

- Created an SD-WAN zone with both WAN interfaces as members, same priority and cost so that traffic is balanced (ECMP).
- Replaced the per-interface default routes with a single static default route pointing at the SD-WAN zone, and a firewall policy from the LAN to that zone with NAT.
- Added a **Performance SLA** (ping health check to a public address) so that a dead link is removed from the routing table automatically.

### Site-to-site IPsec VPN over SD-WAN

- Head office: two tunnels, one per ISP, in dial-up mode. Branch: two static tunnels, one towards each head-office WAN address, with auto-negotiate so that the branch initiates.
- On each side the two tunnel interfaces are grouped in a second SD-WAN zone, with a static route to the remote LAN through that zone, a Performance SLA that pings the remote firewall's LAN address, and an SD-WAN rule that prefers the first ISP.
- Firewall policies in both directions between the LAN and the VPN zone, without NAT.

### Remote access

- Local users in a `VPN_Users` group, a remote-access IPsec tunnel (IKEv2, pre-shared key plus user authentication) that hands out addresses from the VPN pool, and a policy from the tunnel to the LAN.
- FortiClient configured on a client machine to connect to the head office.

## Results

- **WAN failover**: with a continuous ping running from a LAN client, I disabled WAN1. No packet was lost, the SLA showed all traffic moving to WAN2, and the forward-traffic logs showed the change of outgoing interface.
- **Site-to-site**: hosts in the two LANs reach each other through the tunnel. After cutting WAN1, the second tunnel negotiated and traffic moved onto it.

## What I learned

- **Two interfaces in the same subnet are refused by default.** FortiOS wants each interface in its own subnet to route unambiguously; because my lab put both WANs on one host-only network, I had to enable `allow-subnet-overlap` from the CLI.
- **An interface cannot join an SD-WAN zone while it is still referenced** by a firewall policy or a static route — those have to be removed first.
- **Only one of the two site-to-site tunnels is up at a time.** Both tunnels target the same remote subnet, so the firewall keeps a single active path; the second one only negotiates when the first fails. The failover test confirmed this is the expected behaviour, not a fault.
