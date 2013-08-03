/*todo

+  servo measurements a bit small, increased by 0.2. not tested
+  servo wire hole too small
  servo mount slot too small - check cnc - esp drill diameter
  how mount pcb without screws in back? (tap a thread, go through the weight
  make cam smaller, so hangers can go over it?
+  make slot as close to pen hole as possible, otherwise movement is wasted
  servo mount should have rounded edges?
+  round the top of the leaf spring so it doesn't dig 

*/
include <servos.scad>
include <../case/globals.scad>
include </home/mattvenn/cad/MCAD/shapes.scad>
include </home/matthew/work/cad/MCAD/shapes.scad>
$fa = 2.5; //min angle: make large circles smoother
$fs=1.0; //min fragment size, make small circles smoother
//measured
pcb_dist=42;
bolt_r = 2.5/2; //for tapping
pen_holder_r = 30/2;
clearance=0.2;
drill_r = 1+clearance;
servo_dim = [12.5-laser_width, 23.2-laser_width,19.5];
servo_w = servo_dim[0];
servo_h = servo_dim[1];
servo_r = 4.8/2; //axle of the motor
servo_cam_to_holder = 11.2; //distance between one face of the cam and the back shoulder of the servo


//made up
leaf_length = 60;
leaf_thickness = 5; //width of the leaf spring
leaf_clearance = 2; //clearance between spring and walls
leaf_width = 60;
string_attach_height = 30;

servo_x = 5.5;
slot_shift = -5;
cam_y = leaf_length/2 + slot_shift - leaf_thickness/4;
pen_holder_height = 100;
outer_r = 60;

//calculated
hanger_r = pen_holder_r + 5;
servo_y = servo_h+cam_y; 
pen_hole_r = 25/2; //acrylic pipe is 30mm D, which I'll turn down to get a nice fit
echo(str("thickness:",thickness," laser_width:",laser_width));
echo(str("slot width:",thickness-laser_width));
//the bits
module made_gondola()
{
    acrylic() gondola();
    *acrylic() translate([0,0,20 +thickness*2]) rotate([0,0,45])hanger();
    *acrylic() translate([0,0,20 +thickness*3]) rotate([0,0,-180-45])hanger();
    acrylic() pen_holder();
    cam_angle = $t * -90;
    acrylic() translate([servo_x,cam_y,thickness+thickness/2+servo_w/2]) rotate([90,cam_angle,0]) cam();
    color("blue") translate([0,thickness,thickness]) servo();
    translate([0,thickness,0])
    acrylic() servo_mount();
    acrylic() translate([0,0,thickness])leaf_riser();
}
made_gondola();
//translate([0,0,thickness])
*projection() leaf_riser();
*projection() gondola();
*gondola();
*projection() rotate([90,0,0]) servo_mount();
*hanger();
*projection()hanger_washer();

module slot_test()
{
    h = servo_w+3*thickness;
    projection() cube([60,thickness-laser_width,thickness-laser_width],center=true);
}
module acrylic()
{
    color("grey",0.8)
        child();
}
module servo_mount_diff()
{
    servo_mount_w = 60;
    notch_h = 5;
    h = string_attach_height+notch_h;
    translate([0,cam_y+thickness+servo_cam_to_holder,h/2-thickness/2])
        rotate([90,0,0])
            difference()
            {
                minkowski()
                {
                    cube([servo_mount_w,h-drill_r*2,thickness-laser_width],center=true);
                    cylinder(r=drill_r,h=0.1);
                }
                //string notches
                translate([servo_mount_w/2-notch_h,h/2-notch_h/2,0])
                    cube([1.5,notch_h,thickness*2],center=true);
                translate([servo_mount_w/2-notch_h,h/2-notch_h,0])
                    cylinder(r=notch_h/2,h=thickness*2,center=true);
                translate([-servo_mount_w/2+notch_h,h/2-notch_h/2,0])
                    cube([1.5,notch_h,thickness*2],center=true);
                translate([-servo_mount_w/2+notch_h,h/2-notch_h,0])
                    cylinder(r=notch_h/2,h=thickness*2,center=true);

            }

}

module servo_mount()
{
    difference()
    {
        servo_mount_diff();
        translate([0,0,thickness])
            servo();
    }
}

module servo()
{
    alignds420(position=[servo_x,servo_y,thickness/2+6],rotation=[0,-90,90],servo_dim=servo_dim);
    translate([servo_w-drill_r,servo_y-servo_dim[0]/2,thickness/2+6])rotate([0,-90,90])cylinder(r=drill_r*2,h=20,center=true);
}
module pen_holder()
{
    translate([0,0,pen_holder_height/2])
        difference()
        {
            cylinder(r=pen_hole_r,h=pen_holder_height,center=true);
            cylinder(r=pen_hole_r-thickness,h=pen_holder_height*1.5,center=true);
        }
    
}

module pcb_holes()
{
  translate([-pcb_dist/2,0,0])
    cylinder(r=bolt_r,h=thickness*2,center=true);
  translate([+pcb_dist/2,0,0])
  cylinder(r=bolt_r,h=thickness*2,center=true);
}
module slot(l,w)
{
  
  t=thickness*2;
  slot_w =drill_r*2;
      //top
      translate([0,l/2,0])
        cube([w,slot_w,t],center=true);

      //bottom left corner stress hole
*      translate([-w/2,-l/2,0])
        cylinder(r=slot_w*.8,h=t,center=true);

      //bottom right corner stress hole
*      translate([w/2,-l/2,0])
        cylinder(r=slot_w*.8,h=t,center=true);

      //top left corner
      translate([-w/2,l/2,0])
        cylinder(r=slot_w/2,h=t,center=true);

      //top right corner
      translate([w/2,+l/2,0])
        cylinder(r=slot_w/2,h=t,center=true);

      //left side
      translate([-w/2,0,0])
        rotate([0,0,90])
          cube([l,slot_w,t],center=true);

      //right side translate([+w/2,0,0])
        rotate([0,0,90])
          cube([l,slot_w,t],center=true);
}

module leaf_riser()
{
    difference()
    {
    translate([0,leaf_length*0.7*0.25-leaf_clearance*2,0])
    roundedBox(leaf_width-2*leaf_clearance,leaf_length*0.7,thickness,2);
    translate([0,-leaf_thickness,0])
    roundedBox(leaf_width-2*leaf_clearance-2*leaf_thickness,leaf_length-leaf_clearance*2,thickness*2,14);
    }
}
module gondola()
{
  difference()
  {
    //plate
    cylinder(r=outer_r,h=thickness,center=true);
    difference()
    {
    roundedBox(leaf_width,leaf_length,thickness*2,2);
    translate([0,-leaf_thickness-2*leaf_clearance-5,0])
      roundedBox(leaf_width-2*leaf_thickness-4*leaf_clearance,leaf_length+10,thickness*2,14);
    }
    //pen hole
    cylinder(r=pen_hole_r,h=2*thickness,center=true);

    //pcb holes
    translate([0,-outer_r*0.6,0])
      pcb_holes();
    translate([0,thickness,-1])
        servo_mount_diff();

  }
    //leaf springs
    springs();
        
}

module springs()
{
    translate([leaf_width/2-leaf_thickness/2-leaf_clearance,0,0])
        spring();
    translate([-leaf_width/2+leaf_thickness/2+leaf_clearance,0,0])
        spring();
}
module spring()
{
    cylinder(r=leaf_thickness/2,h=thickness,center=true);
    translate([0,-leaf_length/4,0])
    difference()
    {
        cube([leaf_thickness,leaf_length/2,thickness],center=true);
        translate([0,-leaf_length/2.5,0])
            cube([leaf_thickness/3,leaf_length,thickness*2],center=true);
    }

}
/*
module rounded()
{
    translate([-leaf_length/2+leaf_width/2-3*drill_r-clearance,leaf_length/2-leaf_width/2+3*drill_r+clearance,0])
      rotate([0,0,-90])
    difference()
    {
    cube([drill_r*4,drill_r*4,thickness*2],center=true);
    translate([drill_r*2,drill_r*2,0])
      cylinder(r=drill_r*2,h=thickness*4,center=true);
    }
}
*/
module hanger()
{
  color("blue")
  difference()
    {
      hull()
      {
        translate([outer_r/2,0,0])
          cylinder(r=hanger_r/3,h=thickness,center=true);
        cylinder(r=hanger_r,h=thickness,center=true);
      }
      cylinder(r=pen_holder_r+clearance,h=thickness*2,center=true);
      //string hole
      echo(str("string distance=",outer_r/2));
      translate([outer_r/2,0,0])
        cylinder(r=bolt_r+clearance,h=thickness*2,center=true);
    }
}

module hanger_washer()
{
difference()
{

        cylinder(r=hanger_r,h=thickness,center=true);
      cylinder(r=pen_holder_r+clearance,h=thickness*2,center=true);
      }
}
module cam()
{
  radius = servo_w/2+thickness;
  difference()
  {
    translate([0,thickness,0])
    cylinder(r=radius,h=thickness,center=true);
    cylinder(r=servo_r,h=thickness*2.0,center=true);
  }
}

