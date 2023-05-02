# Project Description
The Fetchbot interface allows users to connect to and control a Raspberry Pi based robot "Fetchbot", without internet connection. The connection between a computer and the robot is established through Wifi. 

Please refer to the last section for interface description & editing.

![image](https://user-images.githubusercontent.com/60618118/187421842-e59810de-1c8c-49c3-9af5-bb2beb6852a1.png)

# Installation
This project has been tested on a Windows 10 64-bit machine and a Raspberry Pi 4.

*Presentation & installation video:*

[![Installation video](https://img.youtube.com/vi/bC7nAwIKf-U/0.jpg)](https://www.youtube.com/watch?v=bC7nAwIKf-U)


## Windows

* Install Anaconda Python (Installer in the Google drive: https://drive.google.com/drive/folders/1O0ZvvSjgypUunFu7uR9pzGn0pdYZAEDJ?usp=share_link)


* Navigate to https://github.com/lascientotheque/fetchbot-blockly and click on **code>Download ZIP**. Extract the files once the download is complete.


### Install Python Packages

In the command prompt, enter the following commands:

> cd *"path of the downloaded the fetchbot repository"*

> pip install -r requirements.txt

## Wifi Pairing

On your **Windows PC**, go to Wifi networks and connect to the raspberry_pi_xx access point. 



# Execution

## Windows

The program can be executed from the command prompt with:

> cd *"path of the downloaded the fetchbot repository"*

> python3 main.py

## Raspberry Pi
The program starts automatically on startup (auto login).

To disable the auto start, open a new terminal window and enter:

> CTRL+C

> nano /home/pi/.bashrc

Comment out the two last lines of the file:

> Starting Fetchbot... ress CTRL+C to exit

> #python /home/pi/fetchbot-rpi/main.py

Save and exit the file with CTRL+X.

And reboot:

> sudo reboot

# Notes
Make sure that the Wifi connection is active between the Raspberry Pi and the Windows PC before launching the program on the Windows PC. 


# Interface Description & Editing
The **index.html** file holds 3 iframes:
- Blockly Interface (JS)
- Video & test box (Python Flask)
- AI Classifier (Python Flask)

Code for the Blockly Interface are found in **blockly/demos/code/**.

The html files for the video & text box and the AI classifier are found in **templates/**.

**Main.py** or master program runs a flask server which serves the video & test box and the AI classifier. When the "start" button is pressed on the blockly interface, a POST request with the python translated code is sent to the master program. The master program creates a new **temp.py** python file based on this translated code, which is then executed as subprocess.

The **temp.py** file uses the **fetchbot.py** library in **src/** to send mouvement and text commands by POST requests to the master program, the latter then sends those commands to the robot via serial-over-bluetooth (as only one serial connection can exist at a time).

The image feed is sent from the robot to the master program via the serial-over-bluetooth connection.

The AI classifier allows the user to take image stills from the video feed and save them to a created class. The created classes and images are found in **classes**.

## Adding blocks to blockly

A new block can be created using the Blockly block factory tool in **blockly/demos/blockfactory/index.html**. 

New blocks are created by defining their inputs, fields, types and colours using the drag and drop interface on the left.

![5](https://user-images.githubusercontent.com/60618118/189106393-2c2b5237-c12d-4a67-bbe8-14e4266e8162.png)

The *Block Definition* specifies what the block looks like and the *Generator stub* specifies what the code does (the python line of code associated to it).

Once a new block is created, copy the *Block Definition* (select JavaScript) and the *Generator stub* (select Python), and paste it at the end of **blockly/demos/code/fetchbot.js**. 
```
Blockly.Blocks['print_hello'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("this block prints hello");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};
```
```
Blockly.Python['print_hello'] = function(block) {
  // TODO: Assemble Python into code variable.
  var code = 'print("hello")\n';
  return code;
};
```

To display this block on the blockly interface, add the following line between the `<category name="Fetchbot" colour="#a83236"></category>` tags in **blockly/demos/code/index.html**:
```
<block type="print_hello"></block>
```
