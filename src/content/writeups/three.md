---
# Imported from Obsidian: Three.md
# Draft: incomplete: stops at subdomain discovery, no flag
title: Three
category: Boot2Root
ctf: Hack The Box
date: 2026-08-07
tags:
- boot2root
- hack-the-box
lang: fr
draft: true
imported: true
---

```
nmap -sC -sV 10.129.1.65
```

Deux ports 22 (SSH) et 80 pour HTTP 

```
gobuster dir -u http://10.129.1.65/ -w /usr/share/wordlists/dirb/common.txt
```

On a rien de bon 

```
ffuf -u http://thetoppers.htb -H "Host: FUZZ.thetoppers.htb" -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt -fs 11952
```

Modifier le /etc/hosts 

```
10.129.1.65     thetoppers.htb  s3.thetoppers.htb
```

```
 curl -v http://s3.thetoppers.htb/
```

Sortie

```
Host s3.thetoppers.htb:80 was resolved.
* IPv6: (none)
* IPv4: 10.129.1.65
*   Trying 10.129.1.65:80...
* Established connection to s3.thetoppers.htb (10.129.1.65 port 80) from 10.10.14.72 port 57880 
* using HTTP/1.x
> GET / HTTP/1.1
> Host: s3.thetoppers.htb
> User-Agent: curl/8.19.0
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 404 
< Date: Wed, 20 May 2026 20:16:42 GMT
< Server: hypercorn-h11
< Content-Type: text/html; charset=utf-8
< Content-Length: 21
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: HEAD,GET,PUT,POST,DELETE,OPTIONS,PATCH
< Access-Control-Allow-Headers: authorization,cache-control,content-length,content-md5,content-type,etag,location,x-amz-acl,x-amz-content-sha256,x-amz-date,x-amz-request-id,x-amz-security-token,x-amz-tagging,x-amz-target,x-amz-user-agent,x-amz-version-id,x-amzn-requestid,x-localstack-target,amz-sdk-invocation-id,amz-sdk-request
< Access-Control-Expose-Headers: etag,x-amz-version-id
< 
* Connection #0 to host s3.thetoppers.htb:80 left intact
{"status": "running"}                                   
```
