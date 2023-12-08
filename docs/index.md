# Welcome to SimpleCTE!

SimpleCTE is a simple, easy-to-use, and free database application for managing contacts, organizations, and resources. 
SimpleCTE is designed to be used by Career and Technical Education (CTE) programs, but can be used by anyone who needs to manage contacts, organizations, and resources.

SimpleCTE is written in Python 3.11 and uses PySimpleGUI for its GUI. SimpleCTE uses SQLite for its database.

## Installation

Simply download and run the executable file, found in the [releases](https://github.com/WhoIsConch/SimpleCTE/releases). 
SimpleCTE requires no further installation.

SimpleCTE has not been tested to run on any operating system other than Windows 10 and 11.

## Usage

SimpleCTE consists of two main screens: Search and View screens.

### Search Screen

The Search Screen is a screen in SimpleCTE that is split into two logical screens, one for Organizations and one for 
Contacts. The Search Screen is the first screen that is displayed when SimpleCTE is opened, and can be used to search 
through records to find the one you are looking for. Almost every field in a record can be searched using the Search 
Screen, and results can also be sorted. 

Switching between the Organization and Contact Search Screens can be done by changing the value of the `View:` dropdown
at the top-right of the screen.

### View Screen

The View Screen is a screen in SimpleCTE that displays a single record. The View Screen can be accessed by double-clicking
a record in the Search Screen, or by selecting the `View` option in the alt-click menu of a record. The View Screen can
also be accessed by double-clicking a record in any other table that lists a record.

The View Screen is split into three logical screens, one for Organizations, one for Contacts, and one for Resources.
The View Screen is the main screen for editing records, and can be used to edit almost every field in a record. The View
Screen can also be used to create new records, and to link and unlink records together.

## Examples

For some examples of how to use SimpleCTE, view the [Example Uses](https://github.com/WhoIsConch/SimpleCTE/wiki/Example-Uses) section.