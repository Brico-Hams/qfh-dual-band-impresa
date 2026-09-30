include <qfh_piezas.scad>
PIEZA="ninguna";
module hilo(p1,p2,d=4){hull(){translate(p1)sphere(d=d,$fn=8);translate(p2)sphere(d=d,$fn=8);}}
module espira(R,H,a,z0,col){
  color(col){
    N=40;
    for(s=[0,180]) for(i=[0:N-1]){
      t1=i/N; t2=(i+1)/N;
      hilo([R*cos(a+s+180*t1),R*sin(a+s+180*t1),z0-H*t1],[R*cos(a+s+180*t2),R*sin(a+s+180*t2),z0-H*t2]);
    }
    hilo([R*cos(a),R*sin(a),z0],[3*cos(a),3*sin(a),z0]);
    hilo([-R*cos(a),-R*sin(a),z0],[-3*cos(a),-3*sin(a),z0]);
    hilo([R*cos(a),R*sin(a),z0-H],[-R*cos(a),-R*sin(a),z0-H]);
  }
}
color("white",0.35) translate([0,0,-720]) cylinder(d=30,h=760);
espira(143,650,0,0,"orangered");
espira(135.5,615,90,0,"orange");
espira(45.5,218,0,-30,"royalblue");
espira(43,206,90,-30,"deepskyblue");
// soportes
color("dimgray"){
 translate([0,0,-11]) cruceta_varillas([0,90,180,270],45);
 translate([0,0,-41]) cruceta_uhf([[0,uhf_R_grande],[180,uhf_R_grande],[90,uhf_R_peq],[270,uhf_R_peq]]);
 for(p=[[-325,90],[-307,0],[-615,90],[-650,0]]) translate([0,0,p[0]-11]) rotate([0,0,p[1]]) cruceta_varillas([0,180],90);
 for(p=[[-236,90,uhf_R_peq],[-248,0,uhf_R_grande]]) translate([0,0,p[0]-5]) rotate([0,0,p[1]]) cruceta_uhf([[0,p[2]],[180,p[2]]]);
}
color("burlywood") for(v=[[0,0,143],[90,0,135.5],[180,0,143],[270,0,135.5],[0,-650,143],[180,-650,143],[90,-615,135.5],[270,-615,135.5],[90,-325,143],[270,-325,143],[0,-307,135.5],[180,-307,135.5]])
  translate([0,0,v[1]]) rotate([0,0,v[0]]) translate([17,0,0]) rotate([0,90,0]) cylinder(d=10,h=v[2]-25);
