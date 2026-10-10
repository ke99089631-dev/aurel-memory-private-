@echo off
schtasks /Run /TN "AUREL_ChartServe"
schtasks /Query /TN "AUREL_ChartServe" /FO LIST
