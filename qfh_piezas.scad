// =============================================================
//  QFH doble banda (145.700 / 435.300 MHz) - piezas imprimibles
//  Tubo central 30 mm, brazos de varilla de cortina 10 mm,
//  hilo de cobre 2,5 mm (del cable de 35 mm2 destrenzado).
//
//  Cambia PIEZA para exportar cada STL:
//   "cruceta_vhf"      cruceta superior VHF, 4 brazos   (x1)
//   "barra_vhf"        soporte 2 brazos (inferiores y medios) (x4)
//   "punta"            aislador de punta con pinza de hilo (x12)
//   "grapa"            separador de hilo sobre la varilla (x8)
//   "cruceta_uhf"      cruceta superior UHF completa    (x1)
//   "barra_uhf_grande" soporte inferior UHF espira grande (x1)
//   "barra_uhf_peq"    soporte inferior UHF espira pequena (x1)
//   "todo"             vista de todas las piezas
//  Imprimir en PETG o ASA (el PLA se degrada al sol).
// =============================================================

PIEZA = "todo";

// ---------- parametros ----------
tubo_d    = 30;     // diametro exterior del tubo central
holgura   = 0.4;    // holgura de ajuste (sube a 0.6 si queda duro)
varilla_d = 10;     // diametro de la varilla de cortina
hilo_d    = 2.5;    // diametro del hilo de cobre
tornillo_d = 4.3;   // M4 para fijar al tubo
tuerca_ec  = 7.2;   // M4: entrecaras de la tuerca (+holgura)
tuerca_h   = 3.4;

// Radios UHF (centro del hilo). Calculadora: 48 / 45.5 mm.
// EA1PA redujo el radio UHF ~5 mm; aqui se deja 2,5 mm menos
// como punto medio. Ajusta si lo necesitas.
uhf_R_grande = 48.0 - 2.5;
uhf_R_peq    = 45.5 - 2.5;

$fn = 64;
e = 0.01;

// ---------- piezas base ----------
manguito_h = 22;
manguito_de = tubo_d + 2*holgura + 2*3.2;   // pared 3,2 mm
boss_d = varilla_d + 2*3;                     // pared 3 mm
r_fondo = tubo_d/2 + holgura + 2;             // fondo del alojamiento
r_boss  = r_fondo + 26;                       // alojamiento de 26 mm

// bloque para el tornillo M4 (con tuerca cautiva metida desde arriba)
rt = tubo_d/2 + holgura + 2.5;          // cara interior de la tuerca
xb = rt + tuerca_h + 4;                  // fin del bloque
module bloque_tornillo(ang) {
    rotate([0,0,ang]) translate([0,-7,0]) cube([xb, 14, manguito_h]);
}
module agujero_tornillo(ang) {
    rotate([0,0,ang]) {
        translate([0,0,manguito_h/2]) rotate([0,90,0]) cylinder(d=tornillo_d, h=xb+1);
        translate([rt, -tuerca_ec/2, manguito_h/2 - tuerca_ec/2/cos(30)])
            cube([tuerca_h, tuerca_ec, manguito_h]);
    }
}

module manguito() {
    cylinder(d=manguito_de, h=manguito_h);
}

module cruceta_varillas(angulos, tornillo_ang) {
    difference() {
        union() {
            manguito();
            bloque_tornillo(tornillo_ang);
            for (a = angulos) rotate([0,0,a])
                translate([0,0,manguito_h/2]) rotate([0,90,0]) {
                    cylinder(d=boss_d, h=r_boss);
                }
            // base plana para imprimir sin soportes
            for (a = angulos) rotate([0,0,a])
                translate([0,-boss_d/2,0]) cube([r_boss, boss_d, manguito_h/2]);
        }
        translate([0,0,-e]) cylinder(d=tubo_d + 2*holgura, h=manguito_h + 2*e);
        for (a = angulos) rotate([0,0,a])
            translate([r_fondo,0,manguito_h/2]) rotate([0,90,0])
                cylinder(d=varilla_d + holgura, h=r_boss);
        agujero_tornillo(tornillo_ang);
        // marca de orientacion (muesca en el brazo 0)
        translate([manguito_de/2 - 1, -1, manguito_h - 1.5]) cube([3, 2, 2]);
    }
}

// pinza para el hilo: ranura vertical abierta hacia fuera
module ranura_hilo(largo) {
    // agujero del hilo
    cylinder(d=hilo_d + 0.2, h=largo, center=true);
    // boca de entrada (algo mas estrecha que el hilo: clic)
    translate([0,-(hilo_d*0.8)/2,-largo/2]) cube([10, hilo_d*0.8, largo]);
}

// ---------- aislador de punta (VHF) ----------
// Alojamiento de 30 mm: con la varilla metida 20 mm el hilo queda
// en el radio nominal; metiendola hasta el fondo el radio baja 10 mm.
punta_prof = 30;
punta_hilo = 8;     // del fondo del alojamiento al centro del hilo
module punta() {
    L = punta_prof + punta_hilo + hilo_d/2 + 3;
    difference() {
        union() {
            // cuerpo tumbado: eje de la varilla en X, imprime sobre cara plana
            translate([0,-boss_d/2,0]) cube([L - boss_d/2, boss_d, boss_d]);
            translate([L - boss_d/2, 0, 0]) cylinder(d=boss_d, h=boss_d);
        }
        // alojamiento de la varilla
        translate([-e,0,boss_d/2]) rotate([0,90,0])
            cylinder(d=varilla_d + holgura, h=punta_prof + e);
        // ranura del hilo (vertical cuando esta montada = eje Y aqui)
        translate([punta_prof + punta_hilo, 0, boss_d/2]) rotate([90,0,0])
            rotate([0,0,0]) ranura_hilo(boss_d + 2);
        // tornillo prisionero M3 para fijar la varilla
        translate([punta_prof/2, 0, -e]) cylinder(d=2.8, h=boss_d/2);
    }
}

// ---------- grapa separadora ----------
// abraza la varilla y sujeta el hilo horizontal 12 mm por encima
module grapa() {
    w = 8;
    ri = (varilla_d + holgura)/2;
    difference() {
        union() {
            cylinder(r=ri + 2.5, h=w);
            translate([-3, 0, 0]) cube([6, ri + 12 + hilo_d, w]);
        }
        translate([0,0,-e]) cylinder(r=ri, h=w + 2*e);
        // apertura del clip
        translate([-ri*0.8, -ri - 5, -e]) cube([ri*1.6, ri + 3, w + 2*e]);
        // ranura del hilo a 12 mm del borde de la varilla
        translate([0, ri + 12, w/2]) rotate([0,0,90])
            ranura_hilo(w + 2);
    }
}

// ---------- crucetas UHF (brazos impresos) ----------
module brazo_uhf(R) {
    h = 10; w = 8;
    difference() {
        union() {
            translate([0,-w/2,0]) cube([R, w, h]);
            translate([R,0,0]) cylinder(d=w + 2, h=h);
        }
        translate([R,0,h/2]) rotate([0,0,0]) ranura_hilo(h + 2);
    }
}
module cruceta_uhf(pares) {  // pares = [[angulo, radio], ...]
    difference() {
        union() {
            manguito();
            bloque_tornillo(45);
            for (p = pares) rotate([0,0,p[0]]) brazo_uhf(p[1]);
        }
        translate([0,0,-e]) cylinder(d=tubo_d + 2*holgura, h=manguito_h + 2*e);
        agujero_tornillo(45);
    }
}

// ---------- seleccion ----------
if (PIEZA == "cruceta_vhf")      cruceta_varillas([0,90,180,270], 45);
if (PIEZA == "barra_vhf")        cruceta_varillas([0,180], 90);
if (PIEZA == "punta")            punta();
if (PIEZA == "grapa")            grapa();
if (PIEZA == "cruceta_uhf")      cruceta_uhf([[0,uhf_R_grande],[180,uhf_R_grande],
                                              [90,uhf_R_peq],[270,uhf_R_peq]]);
if (PIEZA == "barra_uhf_grande") cruceta_uhf([[0,uhf_R_grande],[180,uhf_R_grande]]);
if (PIEZA == "barra_uhf_peq")    cruceta_uhf([[0,uhf_R_peq],[180,uhf_R_peq]]);
if (PIEZA == "todo") {
    cruceta_varillas([0,90,180,270], 45);
    translate([150,0,0]) cruceta_varillas([0,180], 90);
    translate([0,110,0]) cruceta_uhf([[0,uhf_R_grande],[180,uhf_R_grande],
                                      [90,uhf_R_peq],[270,uhf_R_peq]]);
    translate([130,100,0]) punta();
    translate([130,130,0]) grapa();
}
