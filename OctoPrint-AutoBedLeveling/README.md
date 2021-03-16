# OctoPrint-AutoBedLeveling

**TODO:** Describe what your plugin does.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/anchor-huang/OctoPrint-AutoBedLeveling/archive/master.zip

**TODO:** Describe how to install your plugin, if more needs to be done than just installing it via pip or through
the plugin manager.

## Configuration

**TODO:** Describe your plugin's configuration options (if any).


## Snapmaker Bed Leveling Commands

- Grid point calculation 
A250 defintion is as below 
    X_DEF_SIZE = 230;
    Y_DEF_SIZE = 250;
    Z_DEF_SIZE = 235;
    MAGNET_X_SPAN = 184;
    MAGNET_Y_SPAN = 204;

    startx = X_DEF_SIZE / 2.0 - MAGNET_X_SPAN / 2.0  => 
    endx = X_DEF_SIZE / 2.0 + MAGNET_X_SPAN / 2.0;
    starty = Y_DEF_SIZE / 2.0 - MAGNET_Y_SPAN / 2.0;
    endy = Y_DEF_SIZE / 2.0 + MAGNET_Y_SPAN / 2.0;

Dial Indictor Offset
 *   In the following example the X and Y offsets are both positive:
 *
 *      +-- BACK ---+
 *      |           |
 *    L |    (+) P  | R <-- probe (47,11)
 *    E |           | I
 *    F | (-) N (+) | G <-- nozzle (10,10)
 *    T |           | H
 *      |    (-)    | T
 *      |           |
 *      O-- FRONT --+
 *    (0,0)

 *  X probe offset from nozzle 37
 *  Y probe offset from nozzle 1

Procedure for Z height calibration 
1. Set the mesh grid (max grid is 11)
    G1029 P5 ==> Set the grid 5x5 
2. Turn-off bed leveling 
    M420 S0
3. Move to grid center point with Z = 15 avoid nozzle touch bed
   Manually adjust Z height to touch bed
   Record Current Z
   Move Z up by 3mm 
    
4. Iterate each grid point (X, Y)
    X, Y=Grid_X - X_probe_offset, Grid_Y - Y_probe_offset
    Dial[X][Y]=Measure Dial Value

5. Calculate Z-offset from Center point 
    Offset[X][Y]=Dial[X][Y]-Dial[center_X][center_Y]
    Mesh[X][Y]=center_Z+Offset[X][Y]
    
    M421 I<xindex> J<yindex> Z<linear>

6. Enable bed leveling 
    M420 V # Print the leveling grid
    M420 S1

7. Store mesh result to EEPROM
    M500