Capitains Nautilus
================

.. image:: https://coveralls.io/repos/github/Capitains/Nautilus/badge.svg?branch=master
    :target: https://coveralls.io/github/Capitains/Nautilus?branch=master
.. image:: https://travis-ci.org/Capitains/Nautilus.svg?branch=master
    :target: https://travis-ci.org/Capitains/Nautilus
.. image:: https://api.codacy.com/project/badge/grade/c76dc6ce6b324246927a49adf7e7fa46
    :target: https://www.codacy.com/app/leponteineptique/Nautilus
.. image:: https://badge.fury.io/py/capitains_nautilus.svg
    :target: https://badge.fury.io/py/capitains_nautilus
.. image:: https://readthedocs.org/projects/capitains-nautilus/badge/?version=latest
    :alt: Documentation
    :target: http://capitains-nautilus.readthedocs.org

Documentation
#############

Documentation will be built in time.

Running Nautilus from the command line
######################################

This small tutorial takes that you have one or more Capitains formated repositories (such as  http://github.com/PerseusDL/canonical-latinLit ) in the folders /home/USERNAME/repository1 where USERNAME is your user session name.


1. (Advised) Create a virtual environment and source it : :code:`virtualenv -p /usr/bin/python3 env`, :code:`source env/bin/activate`
2. **With development version:**
    - Clone the repository : :code:`git clone https://github.com/Capitains/Nautilus.git`
    - Go to the directory : :code:`cd Nautilus`
    - Install the source with develop option : :code:`python setup.py develop`
2. **With production version (not available for now):**
    - Install from pip : :code:`pip install capitains-nautilus`
3. You will be able now to call capitains nautilus help information through :code:`capitains-nautilus --help`
4. Basic setting for testing a directory is :code:`capitains-nautilus --debug /home/USERNAME/repository1`. This can take more than one repository at the end such as :code:`capitains-nautilus --debug /home/USERNAME/repository1 /home/USERNAME/repository2`. You can force host and port through --host and --port parameters.


Source for the tests
####################

Textual resources and inventories are owned by Perseus under CC-BY Licences. See https://github.com/PerseusDL/canonical-latinLit and https://github.com/PerseusDL/canonical-farsiLit
