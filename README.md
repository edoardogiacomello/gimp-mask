# gimp-mask
Plugin for Gimp 2.10 for automatic creation of luminance mask and importing them as layers.

This script is based on the tutorial by Pat David (https://www.gimp.org/tutorials/Luminosity_Masks/)
## Installation

Place the script in your plugin folder, such as:

`/home/<your-username>/.config/GIMP/2.10/plug-ins/plugin-luma-mask.py `


## Usage

1) Create a selection of choice. E.g.
` ctrl + A ``
2) Select `Filters > Lights and Shadows > Mask...`
3) The option panel will appear.

    Options:

        * Number of steps: Control how many iterations to make. The more iterations the more darker and lighter depth is caught by the masks
        * Desaturation Mode: Select the Mode used for creating the masks
        * Apply Mask To: Level creation mode. If "Nothing", masks are only created as channels. Otherwise they are applied to either the source image or desaturated one as new layers.


