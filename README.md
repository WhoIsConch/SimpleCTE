# Welcome to SimpleCTE!

SimpleCTE is a simple, easy-to-use, and open-source database application for managing contacts, organizations, and resources. 
SimpleCTE is designed to be used by Career and Technical Education (CTE) programs, but can be used by anyone who needs to manage contacts, organizations, and resources.

SimpleCTE is written in Python 3.11 and implements PySimpleGUI for its user interface and PonyORM with SQLite for its database operations.

🏅 SimpleCTE is an FBLA NLC 2024 Qualifier

## Installation

SimpleCTE requires Python 3.10 or higher and Python's `virtualenv` package to be installed. Once these requirements are met, SimpleCTE can be run using its `run.ps1` file found in the top-level directory of this repository. This script will create a new virtual environment, install all necessary dependencies, then run the program.

SimpleCTE has not been tested to run on any operating system other than Windows 10 and 11, however, due to the cross-compatibility of PySimpleGUI, the program _should_ run on Linux and Mac systems (with the exception of the `run.ps1` script).

## Usage

SimpleCTE consists of two main screens: Search and View screens.

### Search Screen

The Search Screen is a screen in SimpleCTE that is split into two logical screens, one for Organizations and one for 
Contacts. The Search Screen is the first screen that is displayed when SimpleCTE is opened, and can be used to search 
through records to find the one you are looking for. Almost every field in a record can be searched using the Search 
Screen, and results can also be sorted. 

Switching between the Organization and Contact Search Screens can be done by changing the value of the `View` dropdown
at the top-right of the screen.

### View Screen

The View Screen is a screen in SimpleCTE that displays a single record. The View Screen can be accessed by double-clicking
a record in the Search Screen, or by selecting the `View` option in the alt-click menu of a record. The View Screen can
also be accessed by double-clicking a record in any other table that lists a record.

The View Screen is split into three logical screens, one for Organizations, one for Contacts, and one for Resources.
The View Screen is the main screen for editing records, and can be used to edit almost every field in a record. The View
Screen can also be used to create new records, and to link and unlink records together.

## Examples

For some examples of how to use SimpleCTE, view the [Example Uses](https://github.com/WhoIsConch/SimpleCTE/wiki/Example-Uses) section of the Wiki.
