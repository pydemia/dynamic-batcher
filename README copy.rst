.. .. image:: https://unipy.readthedocs.io/en/latest/_images/logo_white_background.svg
..     :width: 400px
..     :alt: unipy logo
..     :align: center


|Travis|_  |AppVeyor|_  |Coveralls|_  |Readthedocs|_   
|PyPi|_  |Python39|_  |Python310|_ 


.. |Travis| image:: https://travis-ci.org/pydemia/unipy.svg?branch=master
.. _Travis: https://travis-ci.org/pydemia/unipy

.. |AppVeyor| image:: https://ci.appveyor.com/api/projects/status/github/pydemia/unipy?branch=master&svg=true
.. _AppVeyor: https://ci.appveyor.com/project/pydemia/unipy/history

.. |Coveralls| image:: https://coveralls.io/repos/github/pydemia/unipy/badge.svg?branch=master&service=github
.. _Coveralls: https://coveralls.io/github/pydemia/unipy

.. |Readthedocs| image:: https://readthedocs.org/projects/unipy/badge/?version=latest
.. _Readthedocs: http://unipy.readthedocs.io/en/latest/?badge=latest

.. |PyPi| image:: https://badge.fury.io/py/unipy.svg
.. _PyPi: https://badge.fury.io/py/unipy.svg

.. |Python39| image:: https://img.shields.io/badge/python-3.9-blue.svg 
.. _Python39: https://badge.fury.io/py/unipy.svg 

.. |Python310| image:: https://img.shields.io/badge/python-3.10-blue.svg 
.. _Python310: https://badge.fury.io/py/unipy.svg 



dynamic_batcher
===============

`dynamic_batcher` is designed for inferencing DL models using GPU and enforces model's concurrency.

Installation
============

::

    pip install dynamic_batcher



Quickstart
==========


Additional Requirements
-----------------------

::

    pip install -r requirements-test.txt



Run
---


* redis

..  code-block::



Test
---


item
'''''''''''''


Usage
=====

::

    from dynamic_batcher import DynamicBatcher, BatchProcessor



