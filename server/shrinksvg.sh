#!/bin/bash
feeds=$(\ls ../tmp)
for feed in $feeds ; do
  echo $feed
  cd /home/matt/polargraphenergymonitor/tmp/$feed
  if [ -f concat.svg ]; then
    file="concat.svg"
  elif [ -f tree.svg ]; then
    file="tree.svg"
  fi
  echo $file
  mv $file $file.big
  grep -v '^$' $file.big > $file
  rm $file.big
done
exit

