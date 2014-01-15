include <../case/stepper.scad>
include <../case/globals.scad>
include </home/mattvenn/cad/MCAD/shapes.scad>
include </home/matthew/work/cad/MCAD/shapes.scad>

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

//space for the perpendicalar wire guide
slot_space = thickness * 2;
height = switch_length + slot_space;
screw_r = 2;
clearance = 0.2;
//wire z
wire_z = 5;
wire_r = 0.8 / 2;
guide_height = thickness + wire_z + 3; //wire_z * 2;

*projection() wireguide();
made_wireguide();
made_mount_plate();
*projection() made_mount_plate();
module made_mount_plate()
{
    difference()
    {
        mount_plate();
        made_wireguide(true);
    }
}
module made_wireguide(boolean)
{
    translate([0,height/2-thickness/2-thickness,guide_height/2-thickness/2])
    rotate([90,0,0])
    wireguide(boolean);
}
module wireguide(boolean)
{
    assign(thickness = thickness - clearance)
    {
        difference()
        {
            union()
            {
            roundedBox(width,guide_height,thickness,round_radius);
            //only rounded on the top
            translate([0,-guide_height/2+thickness/2,0])
                cube([width,thickness+0.01,thickness+0.01],center=true);
            }
            hull()
            {
            translate([5+wire_clearance/2,-guide_height/2+thickness+wire_z,0])
                cylinder(r=wire_r,h=thickness*2,center=true);
            translate([width+wire_clearance/2,-guide_height/2+thickness+wire_z,0])
                cylinder(r=wire_r,h=thickness*2,center=true);
            }
            //the dibbit
            translate([0,-guide_height/2+thickness/2,0])
                if( boolean )
                    cube([width/3+clearance,thickness,thickness*2],center=true);
                else
                    cube([width/3,thickness,thickness*2],center=true);
        }
    }
}

module mount_plate()
{
    difference()
    {
    roundedBox(width,height,thickness,round_radius);

    translate([ width/2-screw_edge_width-edge_clearance,
                height/2-edge_clearance-m3_bolt_r-slot_space,
                0])
    {
        //hole for mounting the roller
        cylinder(r=m3_bolt_r,h=thickness*2,center=true);
        //switch mount holes
        translate([-switch_offset_x,switch_offset_y,0])
            switch_holes();
    }
    //mounting holes
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
