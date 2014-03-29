//nema 17 motor mounting is 31mm
mount_dist = 31/2;
tap_hole_r = 3.5 / 2;

include <../case/globals.scad>
include </home/mattvenn/cad/MCAD/shapes.scad>
include </home/matthew/work/cad/MCAD/shapes.scad>
include </home/matt/cad/MCAD/shapes.scad>

spring_l = stepper_width / 2;
spring_w = tap_hole_r * 3;
offset = 6;
projection() pickup();
module pickup()
{
    difference()
    {
        roundedBox(stepper_width,stepper_width,thickness,round_radius);
        //mount holes
        translate([mount_dist,mount_dist,0])
            cylinder(r=m3_bolt_r,h=thickness*2,center=true);
        translate([-mount_dist,mount_dist,0])
            cylinder(r=m3_bolt_r,h=thickness*2,center=true);
        translate([-mount_dist,-mount_dist,0])
            cylinder(r=m3_bolt_r,h=thickness*2,center=true);
        translate([mount_dist,-mount_dist,0])
            cylinder(r=m3_bolt_r,h=thickness*2,center=true);

        //tap hole
        cylinder(r=tap_hole_r,h=thickness*2,center=true);

        //spring shape
        translate([spring_l/2-offset,spring_w,0])
            roundedBox(spring_l,round_radius,2*thickness,1);
        translate([spring_l/2-offset,-spring_w,0])
            roundedBox(spring_l,round_radius,2*thickness,1);
        translate([-offset+round_radius/2,0,0])
        roundedBox(round_radius,spring_w*2+round_radius,2*thickness,1);
    }
}
