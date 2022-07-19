# sky130_via_generator

This Python script controlled with a GUI is used to generate layout of vias or via stacks for metals 1 through 5 in a form of .mag files for usage in the magIC VLSI layout tool with the open source SkyWater 130nm technology. The vias/via stacks are DRC clean and feature at least two vias between all of needed metal layers for the via or via stack in the layout for ensuring a better yield.

# Prerequisites:

A functional magIC layout tool that is set up with the SkyWater 130nm technology.

I needed these on an Ubuntu machine.

  Packages:
  
qt5-default (installed via 'apt')
    
    apt install qt5-default

opencv--python (installed via 'pip')

    pip install opencv--python
    
  Other:
  
Make sure your .magicrc file is present in the location of this script.
 
# UI elements:

  Destination path - Used to set the path to where the .mag files of generated vias/via stacks will be saved. By default it's set to the run path of this script.
  
  
  Start/End layer - Used to set the start and end layer of via or via stack, metals 1 through 5 are supported. Start layer must be lower than end layer.
  
  
  Width/Height - Used to set the dimensions of the via or via stack. If a via of set dimensions can't be made DRC clean or it would require only one via of any needed type of vias the dimensions will be increased to make DRC clean and/or fit at least two vias of any needed type for set start and end layers.
  
  
  Generate - Click this button when you are ready to generate specified via.
  
  
  Log - Text log of all actions and errors. Wipes on script end.
 
