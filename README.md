# sky130_via_generator

This Python script controlled with a GUI is used to generate layout of vias or via stacks for metals 1 through 5 in a form of .mag files for usage in the magIC VLSI layout tool with the open source SkyWater 130nm technology. The vias/via stacks are DRC clean and feature at least two vias between all of needed metal layers for the via or via stack in the layout for ensuring a better yield.

![UI image](./images/ui.png?raw=true)

![Layout image](./images/layout.png?raw=true)

# Prerequisites:


qt5-default (installed via 'apt')
    
    apt install qt5-default

opencv--python (installed via 'pip')

    pip install opencv--python

  

 
# UI elements:

  Destination path - Used to set the path to where the .mag files of generated vias/via stacks will be saved. By default it's set to the run path of this script.
  
  
  Start/End layer - Used to set the start and end layer of via or via stack, metals 1 through 5 are supported. Start layer must be lower than end layer.
  
  
  Width/Height - Used to set the dimensions of the via or via stack. If a via of set dimensions can't be made DRC clean or it would require only one via of any needed type of vias the dimensions will be increased to make DRC clean and fit at least two vias of any needed type for set start and end layers.
  
  
  Generate - Click this button when you are ready to generate specified via.
  
  
  Log - Text log of all actions and errors. Not saved locally, wipes on script end.
 
