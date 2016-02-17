# simpletree.py

This is a simple drop-in for `lxml.etree`. I've decided to write it for one of my scripts,
so it wouldn't depend on an lxml package, which is sometimes hard to install.

The module implements `Element`, `SubElement` and `ElementTree` methods, and parsing
and printing functions. It doesn't support namespaces, XPath, schemas and anything complex.
Nearly everything mentioned in the lxml tutorial is supported. Be careful with parsing
big files: the module reads them into strings before parsing.

During the development I've found the built-in `xml.etree.cElementTree` (and `ElementTree`)
to be an adequate replacement for `lxml.etree`, so I'm using that now. But still, this
module is good when you process small chunks of XML.

## TODO

* DocType parsing
* Proper creation of ElementTree from a root Element
* `fromstring()`

## Author and License

Written by Ilya Zverev, licensed WTFPL.
