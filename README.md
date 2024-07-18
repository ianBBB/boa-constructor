## Boa Construtor - An Overview

Hello and thanks for dropping in to check out Boa Constructor. Boa Constructor is an IDE and was originally written in 1999. It runs in Python and uses wxPython for its GUI elements and controls. In 1999, Python and wxPython were very different and have evolved over the itervening time. As such, Boa Constructor will not run on current releases of Python or wxPython. This project was created to "uplift" the code to get Boa working again in modern programming environments.

Boa Constructor is described as a Rapid Application Development tool. Apart from features common to most IDEs such as a full-featured editor, a built-in debugger, TODO functions, Bookmarking, etc Boa also features a GUI-based GUI builder. This means you can graphically build your applications window frame, its menus, its toolbars and buttons, its text entry areas and other controls. There are many built=in wxPython controls available for use in your application; colour picker, Directory Navigation dialogue and file selection, various dialogue boxes to communicate with your user. wxPython has many other controls like radio buttons, spinners, sliders, combo boxes, etc all available for you to pick-and-click into your application.

Boa Constructor presumes your application will operate in the Model-View-Controller framework. Part of the basic design flow in Boa is to select controls and lay them out graphically to make up you user interface and select the events they generate that need to be managed. As such, a project should start its life in Boa Constructor and continue to completion. It is difficult to migrate an existing program into Boa.

## Boa Construtor - The Project

The project is on-going. There are still many parts of Boa that are not yet functional but most of the basics are there for you to get started. There is enough functionality to complete the original Boa Constructor tutorial activity that demonstrates how to use Boa to create basic applications. More functionaity will be available in later releases as I get more working. You can watch how things are progressing by going to the *Discussion* section (in the menu near the top of the page) and look for **"Day-by-Day Progress Reporting Diary"**. Despite the title, updates are approximately weekly. Don't forget to click on the *Newest* button to see the latest updates.

## Installation

There are three basic steps it get Boa Constructor working. They are;
1. Install Python (version 3.12.1 or better)
2. Install wxPython (version 4.2.1 or better)
3. Download Boa Constructor and do final setting up, if needed.

### Installation - Windows 11

Windows does not come with Python so if you do not have it already, you will need to install it. There are several resources on the internet that describe how to do this. The following is a minimalist explanation. Go to the [python.org](https://www.python.org/) website and select Download from the menu. You will see a box titled "Download For Windows" with a button to start the download. Click it to download Python.

Once the download is complete, double click on it to commence the installation process. Accept all the default settings however there is one variation required. You need to tick the "Add Python to Path" box, like this;

<img width="498" alt="python install tick box" src="https://github.com/user-attachments/assets/81af380b-617f-4ad9-8463-e50116295b14">

To install wxPython, use the #pip# tool. Open a terminal window and use the command;
>pip install -U wxPython

(you may be asked to upgrade #pip# . The command to do this will be given to you)

Finally, to download Boa Constructor, go to the github website and search for "ianBBB/boa-constructor" 

If you have the desire and skill to help resurrect Boa Constructor, I would love to hear from you.

Ian Baker
June 2024
