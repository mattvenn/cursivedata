#!/bin/bash
cd /home/matt/polargraphenergymonitor/server
mv concat.svg concat.svg.big
grep -v '^$' concat.svg.big > concat.svg
rm concat.svg.big
