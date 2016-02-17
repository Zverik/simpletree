#!/usr/bin/env python
import simpletree as etree

def test(data, tmpl):
  if str(data) != tmpl:
    print data, "<=", tmpl

# http://lxml.de/tutorial.html
root = etree.Element("root")
test(root.tag, "root")
root.append( etree.Element("child1") )
child2 = etree.SubElement(root, "child2")
child3 = etree.SubElement(root, "child3")
print etree.tostring(root, pretty_print=True)
child = root[0]
test(child.tag, "child1")
test(len(root), "3")
test(root.index(root[1]), "1")
children = list(root)
for child in root:
  print child.tag
print "^^^ child1 child2 child3"
root.insert(0, etree.Element("child0"))
start = root[:1]
end   = root[-1:]
test(start[0].tag, "child0")
test(end[0].tag, "child3")
test(etree.iselement(root), "True")
# root[0] = root[-1] - not supported!
test(root is root[0].getparent(), "True")
test(root[0] is root[1].getprevious(), "True")
test(root[1] is root[0].getnext(), "True")

# http://lxml.de/tutorial.html#elements-carry-attributes-as-a-dict
root = etree.Element("root", interesting="totally")
test(etree.tostring(root), "<root interesting=\"totally\"/>")
test(root.get("interesting"), "totally")
test(root.get("hello"), "None")
root.set("hello", "Huhu")
test(root.get("hello"), "Huhu")
test(sorted(root.keys()), "['hello', 'interesting']")
for name, value in sorted(root.items()):
  print('%s = %r' % (name, value))
attributes = root.attrib
# print attributes["interesting"], "<= totally" - KeyError
test(attributes.get("no-such-attribute"), "None")
attributes["hello"] = "Guten Tag"
test(attributes["hello"], "Guten Tag")
test(root.get("hello"), "Guten Tag")

# http://lxml.de/tutorial.html#elements-contain-text
root = etree.Element("root")
root.text = "TEXT"
test(root.text, "TEXT")
test(etree.tostring(root), "<root>TEXT</root>")

html = etree.Element("html")
body = etree.SubElement(html, "body")
body.text = "TEXT"
test(etree.tostring(html), "<html><body>TEXT</body></html>")
br = etree.SubElement(body, "br")
test(etree.tostring(html), "<html><body>TEXT<br/></body></html>")
br.tail = "TAIL"
test(etree.tostring(html), "<html><body>TEXT<br/>TAIL</body></html>")
test(etree.tostring(br), "<br/>TAIL")
test(etree.tostring(br, with_tail=False), "<br/>")

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
test(d.getroottree().getroot().tag, "root")
tree = etree.ElementTree(d)
test(tree.getroot().tag, "d")
test(etree.tostring(tree), "<d><e/></d>")
element = tree.getroot()
test(element.tag, "d")
test(element.getparent().tag, "root")
test(element.getroottree().getroot().tag, "root")
test(b.getparent() == root, "True")
test(b.getnext().tag, "c")
test(c.getprevious().tag, "b")
test([ child.tag for child in root ], "['a', 'b', 'c', 'd']")
test([ el.tag for el in root.iter() ], "['root', 'a', 'b', 'c', 'd', 'e']")
test([ child.tag for child in root.iterchildren() ], "['a', 'b', 'c', 'd']")
test([ child.tag for child in root.iterchildren(reversed=True) ], "['d', 'c', 'b', 'a']")
test([ sibling.tag for sibling in b.itersiblings() ], "['c', 'd']")
test([ sibling.tag for sibling in c.itersiblings(preceding=True) ], "['b', 'a']")
test([ ancestor.tag for ancestor in e.iterancestors() ], "['d', 'root']")
test([ el.tag for el in root.iterdescendants() ], "['a', 'b', 'c', 'd', 'e']")
test([ child.tag for child in root.iterchildren('a') ], "['a']")
test([ child.tag for child in d.iterchildren('a') ], "[]")
test([ el.tag for el in root.iterdescendants('d') ], "['d']")
test([ el.tag for el in root.iter('d') ], "['d']")
test([ el.tag for el in root.iter('d', 'a') ], "['a', 'd']")

# http://lxml.de/tutorial.html#serialisation
root = etree.XML('<root><a><b/></a></root>')
test(etree.tostring(root), "<root><a><b/></a></root>")
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
test(tree.docinfo.xml_version, "1.0")
test(tree.docinfo.doctype, "<!DOCTYPE root SYSTEM \"test\">")
print etree.tostring(tree)

# http://lxml.de/tutorial.html#parsing-from-strings-and-files
root = etree.XML("<root>data</root>")
test(root.tag, "root")
test(etree.tostring(root), "<root>data</root>")
from io import BytesIO
some_file_like_object = BytesIO("<root>data</root>")
tree = etree.parse(some_file_like_object)
test(etree.tostring(tree), "<root>data</root>")
