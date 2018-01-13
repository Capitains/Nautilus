Capitains Nautilus
==================

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
.. image:: https://zenodo.org/badge/45260156.svg
   :target: https://zenodo.org/badge/latestdoi/45260156
.. image:: https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg
    :alt: License: MPL 2.0
    :target: https://opensource.org/licenses/MPL-2.0

Documentation
#############

CapiTainS Nautilus provides a Flask extension to build upon MyCapytain resolver. The finale goal of the application, built
upon `MyCapytain <https://github.com/capitains/MyCapytain>`_, is to serve either as a Web-API provider (Currently supporting
CTS, partly DTS. OAI-PMH and a Sparql endpoint are scheduled.) These API can be used to access portion of or complete texts
using standards. Metadata are exposed as well.

A second goal of Nautilus is to serve as a cache wrapper for resolver, in order to speed up serving texts for user interfaces
such as `Nemo <https://github.com/capitains/flask-capitains-nemo>`_ .

A known implementation can be found at `the University of Leipzig <http://cts.dh.uni-leipzig.de/api/cts>`_ . You can find the
set-up files on `Github <https://github.com/OpenGreekAndLatin/leipzig_cts>`_

Trying Nautilus with a test dataset example
###########################################

With Python 3 only !

.. code-block:: shell

    git clone https://github.com/Capitains/Nautilus.git
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    python app.py

Now go to http://localhost:5000 and check out http://localhost:5000/api/cts , http://localhost:5000/api/dts/collections,
http://localhost:5000/api/cts?request=GetValidReff

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
