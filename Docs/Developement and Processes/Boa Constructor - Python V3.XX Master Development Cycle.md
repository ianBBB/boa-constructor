# <u>Actvities for Staging Updates to Master Files</u>

1. Update these variables in the following files in the Config directory.
   - Explorer.gtk.cfg
   - Explorer.msw.cfg
   - Explorer.mac.cfg
   1. The _openfiles_ variable should be set to _openfiles = []_ in these files;

   2. Delete entries in _bookmarks_ but leave the root entry in there.

   3. Delete entries in _recentfiles_ with _recentfiles = []_
2. In the Boa Consructor root directory, update the version number in \__version__.py
3. In Config directory, set the _pythonInterpreterPath_ variable in _prefs_rc.py_ to _pythonInterpreterPath = ''_ (that is, two single quote marks)
>>>>>>> Boa is Bonza !!!
