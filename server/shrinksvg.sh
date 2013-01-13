#!/bin/bash
cd /home/matt/polargraphenergymonitor/tmp/46756
mv concat.svg concat.svg.big
grep -v '^$' concat.svg.big > concat.svg
rm concat.svg.big
