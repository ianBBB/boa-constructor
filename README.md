# Boa Constructor
## An Overview

Hello and thanks for dropping in to check out Boa Constructor. Boa Constructor is an IDE originally written in 1999. It runs in Python and uses wxPython for its GUI elements and controls. In 1999, Python and wxPython were very different and have evolved over the itervening time. So much so that the original Boa Constructor code will no longer run on current releases of Python or wxPython. This project was created to "uplift" the code to get Boa working again in modern programming environments.

Boa Constructor is described as a Rapid Application Development tool. Apart from features common to most IDEs such as a full-featured editor, a built-in debugger, TODO functions, Bookmarking, etc Boa also features a GUI-based GUI builder. This means you can graphically build your applications window frame, its menus, its toolbars and buttons, its text entry areas and other controls. There are many built=in wxPython controls available for use in your application; colour picker, Directory Navigation dialogue and file selection, various dialogue boxes to communicate with your user. wxPython has many other controls like radio buttons, spinners, sliders, combo boxes, etc all available for you to pick-and-click into your application.

Boa Constructor presumes your application will operate in the Model-View-Controller framework. Part of the basic design flow in Boa is to select controls and lay them out graphically to make up you user interface and select the events they generate that need to be managed. As such, a project should start its life in Boa Constructor and continue to completion. It is difficult to migrate an existing program into Boa.

The project is ongoing. There are still many parts of Boa that are not yet functional but most of the basics are there for you to get started. There is enough functionality to complete the original Boa Constructor tutorial activity that demonstrates how to use Boa to create basic applications. More functionality will be available in later releases as I get more of the application working.

If you have the desire and skill to help resurrect Boa Constructor, we would love to hear from you.


## Current Build Notes (Phoenix Widgets)

This build adds a new **Phoenix** palette page with modern wxPython controls where available on your platform/build.

Added palette widgets include:
- wx.dataview.DataViewCtrl
- wx.dataview.DataViewListCtrl
- wx.dataview.TreeListCtrl
- wx.adv.CommandLinkButton
- wx.adv.HyperlinkCtrl
- wx.adv.BitmapComboBox
- wx.adv.TimePickerCtrl
- wx.adv.BannerWindow
- wx.ribbon.RibbonBar / RibbonPage / RibbonPanel / RibbonButtonBar
- wx.aui.AuiNotebook / AuiToolBar
- wx.propgrid.PropertyGrid / PropertyGridManager / PropertyGridCtrl
- wx.ActivityIndicator
- wx.RearrangeList / wx.RearrangeCtrl
- wx.InfoBar

Non-visual utility additions:
- wx.aui.AuiManager
- wx.adv.NotificationMessage

Palette help button behavior has been updated so that when a component is selected, help lookup can use module-qualified wx class names (for example `wx.dataview.DataViewCtrl`) in addition to simple class names.


## Installation

There are **two** approaches to installing Boa Constructor.

A manual installation is where you install Python and wxPython directly on your machine then download and start Boa Constructor. This method is suitable for Windows, selected Linux distros and MacOS. Use this link to get instructions for a [manual installation](#manual-installation)

UV creates a virtual environment, downloads required python and wxPython packages to allow Boa Constructor to run. This method is best on Windows and make for simpler, less technical installation. For instructions on using UV, use this link [Install with UV](#installation-with-uv)

## Manual Installation

There are three basic steps it get Boa Constructor working. They are;
1. Install Python (version 3.09.1 or better)
2. Install wxPython (version 4.2.2 or better)
3. Download Boa Constructor and do final setting up, if needed.

### Installation - Windows 11

Windows does not come with Python so if you do not have it already, you will need to install it. There are several resources on the internet that describe how to do this. The following is a minimalist explanation. Go to the [python.org](https://www.python.org/) website and select Download from the menu. You will see a box titled "Download For Windows" with a button to start the download. Click it to download Python.

Once the download is complete, double click on it to commence the installation process. Accept all the default settings however there is one variation required. You need to tick the "Add Python to Path" box, like this;

<img width="498" alt="python install tick box" src="https://github.com/user-attachments/assets/81af380b-617f-4ad9-8463-e50116295b14">

To install wxPython, use the *pip* tool. Open a terminal window and use the command;
>pip install -U wxPython

(you may be asked to upgrade *pip* . The command to do this will be given to you)

Finally, to download Boa Constructor, go to the [github website](https://github.com/) and search for "ianBBB/boa-constructor". This should result in just one link. Click on this link to go to the project. Use the green button marked "Code" to download the ZIP file containing Boa Constructor. Save or move the ZIP file to a convenient location (a folder in My Documents would be suitable). Unzip the file. Extract the ZIP file.

Alternatively, if you want to use Git to get the source code.

1. Using the command line:
   Navigate to the directory where you want to clone the repository and run:
```bash
git clone https://github.com/ianBBB/boa-constructor
```

### Starting Bos Constructor 
To start Boa Constructor, go to the root folder and find the Boa file 
(called "Boa.py", it is 30K in size). 
Double click on this file to open Boa Constructor.
### Installation - Other
Installation instructions for Linux (Ubuntu) and Mac coming soon.


## Installation With UV

### Getting The Source Code

  
#### Downloading the ZIP file
1. Go to the GitHub page: https://github.com/ianBBB/boa-constructor
2. Use the green button marked "Code" to download the ZIP file containing Boa Constructor.
3. Save the ZIP file to your local machine in a directory of your choice.
4. Extract the contents of the ZIP file to a directory on your local machine.

### UV setup.
This project is managed with UV - An extremely fast Python package and project manager, written in Rust. 

Go to the root directory of the files you just extracted. Run the appropriate bootstrap script to install UV on your system.
- Windows: `bootstrap.bat`
- Linux / MacOS: `./bootstrap.sh`

This script will:
1. Download the correct version of Python
2. Set up a virtual environment
3. Install the required dependencies

#### Linux Build Dependencies (Fedora / RHEL)
If compiling wxPython from source (such as on Fedora with newer Python versions):
```bash
sudo dnf install gcc-c++ make pkgconf-pkg-config gtk3-devel webkit2gtk4.1-devel mesa-libGL-devel mesa-libGLU-devel libnotify-devel gstreamer1-plugins-base-devel
```

#### Verifying UV Installation
1. In a new command prompt / terminal window
2. Run `uv self version` to confirm UV is installed




### Installing/Running Boa Constructor
#### Simple
Run the provided script for your platform. 

- Windows: `run.bat`
- Linux / MacOS: `./run.sh`

#### Using CLI - Windows/MacOS/Linux
1. Open a command prompt / terminal window
2. Navigate to the directory where you cloned or extracted the repository
3. Run the following command
```commandline
uv run Boa.py
```
#### In Windows;
In Windows, you can simply double click on the file in File Manager.

