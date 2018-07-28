#!/usr/bin/env python
'''
Gimp plugin "Luminosity Mask"

Copyright 2018 Edoardo Giacomello (edoardo.giacomello1990@gmail.com)
based on "GIMP - Luminosity Masks" by Pat David

License:

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  The GNU Public License is available at
  http://www.gnu.org/copyleft/gpl.html
'''

from gimpfu import *

def channel_to_layer(img, source_layer, channel, name, parent, intersect_with=None):
    new_layer = pdb.gimp_layer_copy(source_layer, True)
    if intersect_with is not None:
        pdb.gimp_channel_combine_masks(channel, intersect_with, 3, 0, 0)
    pdb.gimp_image_select_item(img, CHANNEL_OP_REPLACE, channel)
    mask=new_layer.create_mask(ADD_SELECTION_MASK)
    new_layer.add_mask(mask)
    pdb.gimp_item_set_name(new_layer, name)
    pdb.gimp_image_insert_layer(img, new_layer, parent, 0)

def create_dark_channel(img, light_channel, name):
    #subtract (1) the light channel from the current selection
    pdb.gimp_image_select_item(img, 1, light_channel)
    dark_channel = pdb.gimp_selection_save(img)
    pdb.gimp_item_set_name(dark_channel, name)
    return dark_channel

def create_light_channel(img, light_channel, dark_channel, name):
    temp_channel = pdb.gimp_channel_copy(light_channel)
    pdb.gimp_channel_combine_masks(temp_channel, dark_channel, 1, 0, 0)
    pdb.gimp_item_set_name(temp_channel, name)
    pdb.gimp_image_add_channel(img, temp_channel, 0)
    return temp_channel

def create_mid_channel(img, light_channel, dark_channel, name):
    temp_channel = pdb.gimp_channel_copy(light_channel)
    pdb.gimp_channel_combine_masks(temp_channel, dark_channel, 3, 0, 0)
    pdb.gimp_item_set_name(temp_channel, name)
    pdb.gimp_image_add_channel(img, temp_channel, 0)
    return temp_channel

def create_luma_masks(image, drawable, depth=4, mode=1, applyMaskTo=2):
    if pdb.gimp_selection_is_empty(image):
        pdb.gimp_message("You must first select a region to heal.")
        return
    pdb.gimp_image_undo_group_start(image)

    active_layer = pdb.gimp_image_get_active_layer(image)
    active_selection = pdb.gimp_selection_save(image)
    pdb.gimp_item_set_name(active_selection, "active selection")
    desaturated_layer = pdb.gimp_layer_copy(active_layer, True)
    pdb.gimp_item_set_name(desaturated_layer, "Desaturated")
    pdb.gimp_image_insert_layer(image, desaturated_layer, None, 0)
    pdb.gimp_image_set_active_layer(image, desaturated_layer)



    drawable = pdb.gimp_image_get_active_drawable(image)
    pdb.gimp_drawable_desaturate(drawable, mode)
    # Creating channel arrays
    lights = []
    darks = []
    mids = []


    # Creating first "light" channel
    lights.append(pdb.gimp_channel_new_from_component(image, 3, "L"))
    pdb.gimp_image_add_channel(image, lights[0], 0)


    # Creating layer groups
    if applyMaskTo > 0:
        mask_group = pdb.gimp_layer_group_new(image)
        dark_group = pdb.gimp_layer_group_new(image)
        light_group = pdb.gimp_layer_group_new(image)
        mid_group = pdb.gimp_layer_group_new(image)
        pdb.gimp_item_set_name(mask_group, "Luma Levels")
        pdb.gimp_item_set_name(dark_group, "Dark")
        pdb.gimp_item_set_name(light_group, "Light")
        pdb.gimp_item_set_name(mid_group, "Mid")
        pdb.gimp_image_insert_layer(image, mask_group, None, 0)
        pdb.gimp_image_insert_layer(image, dark_group, mask_group, 0)
        pdb.gimp_image_insert_layer(image, light_group, mask_group, 0)
        pdb.gimp_image_insert_layer(image, mid_group, mask_group, 0)



    # Creating "dark" channel by subtracting the lights from the whole image
    pdb.gimp_selection_all(image)
    for i in range(1, depth+1):
        darks.append(create_dark_channel(image, lights[0], "D"*i))
    # Creating corresponding layers
    if applyMaskTo > 0:
        for i, chan in enumerate(darks):
            if applyMaskTo == 1:
                channel_to_layer(image, active_layer, darks[i], "D"*(i+1), dark_group, active_selection)
	    else:
                channel_to_layer(image, desaturated_layer, darks[i], "D"*(i+1), dark_group, active_selection)

    # Creating the other Light channels
    ## Selecting the lights
    pdb.gimp_selection_clear(image)

    # Combining channels - the result is stored in the first channel
    for i in range(1, depth):
        lights.append(create_light_channel(image, lights[i-1], darks[0], "L"*(i+1)))


    # Creating corresponding layers
        # Creating corresponding layers
    if applyMaskTo > 0:
        for i, chan in enumerate(lights):
            if applyMaskTo == 1:
                channel_to_layer(image, active_layer, lights[i], "L" * (i + 1), light_group, active_selection)
	    else:
                channel_to_layer(image, desaturated_layer, lights[i], "L" * (i + 1), light_group, active_selection)
            


    # Creating midtone levels
    # Combining channels - the result is stored in the first channel
    for i in range(1, depth + 1):
        mids.append(create_mid_channel(image, lights[i-1], darks[i-1], "M"*i))


    # Creating corresponding layers
    if applyMaskTo > 0:
        for i, chan in enumerate(lights):
            if applyMaskTo == 1:
                channel_to_layer(image, active_layer, mids[i], "M" * (i + 1), mid_group, active_selection)
	    else:
                channel_to_layer(image, desaturated_layer, mids[i], "M" * (i + 1), mid_group, active_selection)
            

    pdb.gimp_selection_clear(image)
    pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, active_selection)
    pdb.gimp_image_set_active_layer(image, active_layer)
    pdb.gimp_image_undo_group_end(image)


register(
  "python_fu_mask_luma",
  N_("Create Luma Mask for various intensities "),
  "Create Luma Mask for various intensities ",
  "Edoardo Giacomello",
  "Copyright 2018 Edoardo Giacomello",
  "2018",
  N_("Mask..."),
  "RGB*, GRAY*",
  [
  (PF_IMAGE, "image",       "Input image", None),
  (PF_DRAWABLE, "drawable", "Input drawable", None),
  (PF_INT, "depth", "Number of steps:", 4),
  (PF_OPTION,"mode", "Desaturation Mode:",1,["Lightness","Luma","Average","Luminance","Value"]),
  (PF_OPTION,"applyMaskTo", "Apply mask to:",2,["Nothing","Original Image","Desaturated Image"])
  ],
  [],
  create_luma_masks,
  menu="<Image>/Filters/Light and Shadow"
  )

main()
