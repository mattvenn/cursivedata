#!/bin/bash
openscad gondola.scad -D 'export_leaf_riser=true' -x leaf_riser.dxf
openscad gondola.scad -D 'export_servo_mount=true' -x servo_mount.dxf
openscad gondola.scad -D 'export_servo_support=true' -x servo_support.dxf
openscad gondola.scad -D 'export_gondola=true' -x gondola.dxf
openscad gondola.scad -D 'export_cam=true' -x cam.dxf
