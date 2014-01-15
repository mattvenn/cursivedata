include <../case/stepper.scad>
include <../case/globals.scad>
include </home/mattvenn/cad/MCAD/shapes.scad>

wire_clearance = 10;
edge_clearance = 3;
//m3 plastic pcb spacer
sleeve_r = 5/2;
//switch datasheet: http://www.newark.com/pdfs/datasheets/Honeywell_Sensing/V15.pdf
switch_hole_x = 10.3; //distance between holes
switch_hole_y = 22.2; //distance between holes
switch_pretravel = 1.6;
switch_offset_x = 20.6 + sleeve_r + switch_pretravel; //opearating position - distance between top left hole and when the switch turns on, from website: http://sensing.honeywell.com/product%20page?pr_id=45588
echo(switch_offset_x);
switch_offset_y = switch_hole_y - 20.6; //y distance from edge of roller to left hole , this from datasheet
switch_length = 29;

//calculated
screw_edge_width = 10; //amount we need for screwing down
width = switch_offset_x + edge_clearance * 2 + 2 * screw_edge_width;
height = switch_length;
screw_r = 2;
//guessed
bend_width = 2;
wire_height = 6 - bend_width;
guide_height = wire_height * 2;
projection()
    union()
    {
        mount_plate();
        translate([0,+height/2+bend_width/2,0])
        bend();
        translate([0,+height/2+guide_height/2+bend_width,0])
            wireguide();
    }

module bend()
{
    translate([-width/2+width/4,0,0])
    cube([width/3,bend_width*2,thickness],center=true);
}
module wireguide()
{
difference()
{
    roundedBox(width,guide_height,thickness,round_radius);
    hull()
    {
    translate([5+wire_clearance/2,0,0])
        cylinder(r=0.5,h=thickness*2,center=true);
    translate([width+wire_clearance/2,0,0])
        cylinder(r=0.5,h=thickness*2,center=true);
    }
}
}
module mount_plate()
{
    difference()
    {
    roundedBox(width,height,thickness,round_radius);

    //hole for mounting the roller
    translate([width/2-screw_edge_width-edge_clearance,height/2-edge_clearance-m3_bolt_r,0])
    {
        cylinder(r=m3_bolt_r,h=thickness*2,center=true);
        //switch mount holes
        translate([-switch_offset_x,switch_offset_y,0])
            switch_holes();
    }
    translate([5,-height/2-edge_clearance*2-m3_bolt_r*2,-thickness])
        cube([wire_clearance,height,thickness*2]);
    translate([-width/2+screw_edge_width/2,0,0])
        cylinder(r=screw_r,h=thickness*2,center=true);
    translate([+width/2-screw_edge_width/2,0,0])
        cylinder(r=screw_r,h=thickness*2,center=true);
        
    }
}
//draws from top left hole
module switch_holes()
{
    cylinder(r=m3_bolt_r,h=thickness*2,center=true);
    translate([switch_hole_x,-switch_hole_y,0])
        cylinder(r=m3_bolt_r,h=thickness*2,center=true);
}
