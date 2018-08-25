Change logs
===

## 1.0.3 - 23/05/2017

By @ponteineptique

- Updated Flask-Caching dependency to be in sync with Nemo

## 1.0.2 - 15/01/2017

By @ponteineptique

- Fixed a bug in tests where too much log would prevent the real logs to be read on travis
- Fixed a bug where logs would not be caught by .assertLogged ( Issue #60 )
- Fixed a bug introduced by Flask Caching > 1.3.0 ( Issue #62 )
    - Tests were fixed to resolve bugs. Inner working of the application did not change
- Fixed a bug introduced with Werkzeug newer versions ( Issue #62 )
    - Test where failing with FileSystemCache because it always leave one file after clearing (Which is a File Count variable)
- On Travis, added a monthly cronjob to check on dependencies update impact (since we are using some ">=" dependencies selector)

