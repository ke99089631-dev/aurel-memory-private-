# Android Remote Access (Option A: Remote Desktop over Tailscale)

Chairman wants to talk to AUREL + run/build from Android, same as PC.
Decided: **Option A** (remote desktop over Tailscale). Option B (phone chat bridge) = ON HOLD.
Concept confirmed to chairman: all "rooms" share one warehouse (memory/files on disk); B would be a new room sharing the same warehouse; A = the exact same PC screen mirrored to phone.

## Facts
- PC: Windows 11 **Pro** (RDP host supported). Account `user` = local **Administrator**.
- Tailscale up. PC IP **100.73.107.61** (node desktop-d4krhau). Phone **pixel-8-pro** IP **100.78.223.54** (now ONLINE, was 77d offline).
- Tailscale iface = Private; Wi-Fi = Public.

## PC-side done (2026-08-20)
- RDP enabled: `fDenyTSConnections=0`, NLA on (`UserAuthentication=1`), port 3389, `fEnableWinStation=1`.
- **Firewall scoped to Tailscale-only**: rules `RemoteDesktop-UserMode-In-TCP/UDP`, `RemoteDesktop-Shadow-In-TCP` RemoteAddress = `100.64.0.0/10`. So RDP reachable ONLY from the tunnel (not Wi-Fi/internet).

## OPEN ISSUE
- TermService Running but **no listener on 3389** (qwinsta shows no rdp-tcp; netstat no 3389). Restart-Service TermService did NOT bring it up.
- **Fix = REBOOT** (config all correct; listener just needs a clean boot). After reboot, verify: `Get-NetTCPConnection -LocalPort 3389 -State Listen` should show a listener; `qwinsta` should list rdp-tcp.

## Remaining after reboot
- Phone side: (2) Tailscale app logged in (ke99089631@ Google) = done/online. (3) Microsoft "Windows App" -> add PC `100.73.107.61`, user `user`, password = his Windows sign-in password. If `user` rejected, try Microsoft account email `ke99089631@gmail.com`.
- Error 0x204 seen = client couldn't reach host = listener not up (this issue) OR phone not on tunnel.
- After connect works: build phone->PC image handoff (Taildrop / shared folder) so chairman can send photos; I read the file.

## Safety (unchanged)
- Tunnel-only, nothing exposed to open internet. Password is chairman's; AUREL never reads/stores it.
- Live money still double-locked (CHAIRMAN-GO). Prop untouched.
