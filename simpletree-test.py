#!/usr/bin/env python
import simpletree as etree

# http://lxml.de/tutorial.html
root = etree.Element("root")
print root.tag, "<= root"
root.append( etree.Element("child1") )
child2 = etree.SubElement(root, "child2")
child3 = etree.SubElement(root, "child3")
print etree.tostring(root, pretty_print=True)
child = root[0]
print child.tag, "<= child1"
print len(root), "<= 3"
print root.index(root[1]), "<= 1"
children = list(root)
for child in root:
  print child.tag
print "^^^ child1 child2 child3"
root.insert(0, etree.Element("child0"))
start = root[:1]
end   = root[-1:]
print start[0].tag, "<= child0"
print end[0].tag, "<= child3"
print etree.iselement(root), "<= True"
# root[0] = root[-1] - not supported!
print root is root[0].getparent(), "<= True"
print root[0] is root[1].getprevious(), "<= True"
print root[1] is root[0].getnext(), "<= True"

# http://lxml.de/tutorial.html#elements-carry-attributes-as-a-dict
root = etree.Element("root", interesting="totally")
print etree.tostring(root), "<= <root interesting=\"totally\"/>"
print root.get("interesting"), "<= totally"
print root.get("hello"), "<= None"
root.set("hello", "Huhu")
print root.get("hello"), "<= Huhu"
print sorted(root.keys()), "<= ['hello', 'interesting']"
for name, value in sorted(root.items()):
  print('%s = %r' % (name, value))
attributes = root.attrib
# print attributes["interesting"], "<= totally" - KeyError
print attributes.get("no-such-attribute"), "<= None"
attributes["hello"] = "Guten Tag"
print attributes["hello"], "<= Guten Tag"
print root.get("hello"), "<= Guten Tag"

# http://lxml.de/tutorial.html#elements-contain-text
root = etree.Element("root")
root.text = "TEXT"
print root.text, "<= TEXT"
print etree.tostring(root), "<= <root>TEXT</root>"

html = etree.Element("html")
body = etree.SubElement(html, "body")
body.text = "TEXT"
print etree.tostring(html), "<= <html><body>TEXT</body></html>"
br = etree.SubElement(body, "br")
print etree.tostring(html), "<= <html><body>TEXT<br/></body></html>"
br.tail = "TAIL"
print etree.tostring(html), "<= <html><body>TEXT<br/>TAIL</body></html>"
print etree.tostring(br), "<= <br/>TAIL"
print etree.tostring(br, with_tail=False), "<= <br/>"

# http://lxml.de/tutorial.html#tree-iteration
root = etree.Element("root")
etree.SubElement(root, "child").text = "Child 1"
etree.SubElement(root, "child").text = "Child 2"
etree.SubElement(root, "another").text = "Child 3"
print etree.tostring(root, pretty_print=True)
for element in root.iter():
  print "%s - %s" % (element.tag, element.text)
for element in root.iter("another", "child"):
  print "%s - %s" % (element.tag, element.text)
# Iteration over element types, as well as comment and entity classes, are not supported

# http://lxml.de/api.html#trees-and-documents
root = etree.Element("root")
a = etree.SubElement(root, "a")
b = etree.SubElement(root, "b")
c = etree.SubElement(root, "c")
d = etree.SubElement(root, "d")
e = etree.SubElement(d,    "e")
print etree.tostring(root, pretty_print=True)
print d.getroottree().getroot().tag, "=> root"
tree = etree.ElementTree(d)
print tree.getroot().tag, "<= d"
print etree.tostring(tree), "<= <d><e/></d>"
element = tree.getroot()
print element.tag, "<= d"
print element.getparent().tag, "<= root"
print element.getroottree().getroot().tag, "<= root"
print b.getparent() == root, "=> True"
print b.getnext().tag, "=> c"
print c.getprevious().tag, "=> b"
print [ child.tag for child in root ], "=> ['a', 'b', 'c', 'd']"
print [ el.tag for el in root.iter() ], "=> ['root', 'a', 'b', 'c', 'd', 'e']"
print [ child.tag for child in root.iterchildren() ], "=> ['a', 'b', 'c', 'd']"
print [ child.tag for child in root.iterchildren(reversed=True) ], "=> ['d', 'c', 'b', 'a']"
print [ sibling.tag for sibling in b.itersiblings() ], "=> ['c', 'd']"
print [ sibling.tag for sibling in c.itersiblings(preceding=True) ], "=> ['b', 'a']"
print [ ancestor.tag for ancestor in e.iterancestors() ], "=> ['d', 'root']"
print [ el.tag for el in root.iterdescendants() ], "=> ['a', 'b', 'c', 'd', 'e']"
print [ child.tag for child in root.iterchildren('a') ], "=> ['a']"
print [ child.tag for child in d.iterchildren('a') ], "=> []"
print [ el.tag for el in root.iterdescendants('d') ], "=> ['d']"
print [ el.tag for el in root.iter('d') ], "=> ['d']"
print [ el.tag for el in root.iter('d', 'a') ], "=> ['a', 'd']"

# http://lxml.de/tutorial.html#serialisation
root = etree.XML('<root><a><b/></a></root>')
print etree.tostring(root), "<= <root><a><b/></a></root>"
print etree.tostring(root, xml_declaration=True)
print etree.tostring(root, encoding='iso-8859-1')
print etree.tostring(root, pretty_print=True)
# tostring methods are not supported

# http://lxml.de/tutorial.html#the-elementtree-class
root = etree.XML('''\
  <?xml version="1.0"?>
  <!DOCTYPE root SYSTEM "test" [ <!ENTITY tasty "parsnips"> ]>
  <root>
  <a>&tasty;</a>
  </root>
  ''')
tree = etree.ElementTree(root)
print tree.docinfo.xml_version, "<= 1.0"
print tree.docinfo.doctype, "<= <!DOCTYPE root SYSTEM \"test\">"
print etree.tostring(tree)

# http://lxml.de/tutorial.html#parsing-from-strings-and-files
root = etree.XML("<root>data</root>")
print root.tag, "<= root"
print etree.tostring(root), "<= <root>data</root>"
from io import BytesIO
some_file_like_object = BytesIO("<root>data</root>")
tree = etree.parse(some_file_like_object)
print etree.tostring(tree), "<= <root>data</root>"
