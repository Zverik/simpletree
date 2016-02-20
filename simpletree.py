# A drop-in replacement for lxml.etree package.
# Does not support namespaces, xpath and many other features.
# Written by Ilya Zverev, licensed WTFPL.

class DocInfo:
  def __init__(self):
    self.xml_version = None
    self.encoding = None
    self.doctype = None


class ElementTree:
  def __init__(self, root):
    self.root = root
    if root.tree is not None:
      self.docinfo = root.tree.docinfo
    else:
      self.docinfo = DocInfo()

  def getroot(self):
    return self.root


class ElementMatchIterator:
  def __init__(self, first, tag=None, *tags):
    self.first = first
    self.tags = {}
    if tag is not None:
      self.tags[tag] = True
    for tag in tags:
      self.tags[tag] = True
    self.done = False

  def __iter__(self):
    return self

  def _next(self):
    if not self.done:
      self.done = True
      return self.first
    return None

  def next(self):
    while True:
      n = self._next()
      if n is None:
        raise StopIteration()
      if len(self.tags) == 0 or n.tag in self.tags:
        return n

  def __next__(self):
    return self.next()


class ElementDepthFirstIterator(ElementMatchIterator):
  def __init__(self, first, tag=None, inclusive=True, tags=()):
    ElementMatchIterator.__init__(self, first, tag, *tags)
    self.stack = []
    if not inclusive:
      self._next()

  def _next(self):
    if self.first is None:
      return None
    res = self.first
    if len(self.first):
      self.stack.append(self.first)
      self.first = self.first[0]
    elif len(self.stack) > 0:
      nxt = self.first.getnext()
      while nxt is None and len(self.stack) > 0:
        self.first = self.stack.pop()
        nxt = self.first.getnext()
      if len(self.stack) == 0:
        self.first = None
      else:
        self.first = nxt
    else:
      self.first = None

    return res


class ElementChildIterator(ElementMatchIterator):
  def __init__(self, first, tag=None, reversed=False, tags=()):
    ElementMatchIterator.__init__(self, first, tag, *tags)
    self.d = -1 if reversed else 1
    self.i = len(first) - 1 if reversed else 0

  def _next(self):
    if self.i < 0 or self.i >= len(self.first):
      return None
    res = self.first[self.i]
    self.i += self.d
    return res


class SiblingsIterator(ElementMatchIterator):
  def __init__(self, first, tag=None, preceding=False, tags=()):
    ElementMatchIterator.__init__(self, first, tag, *tags)
    self.preceding = preceding

  def _next(self):
    if self.first is None:
      return None
    if self.preceding:
      self.first = self.first.getprevious()
    else:
      self.first = self.first.getnext()
    return self.first


class AncestorsIterator(ElementMatchIterator):
  def __init__(self, first, tag=None, tags=()):
    ElementMatchIterator.__init__(self, first, tag, *tags)

  def _next(self):
    if self.first is None:
      return None
    self.first = self.first.getparent()
    return self.first


class Element:
  def __init__(self, tag, attrib=None, **kwargs):
    self.tag = tag
    self.attrib = {}
    if attrib is not None:
      self.attrib = attrib
    for k, v in kwargs.iteritems():
      self.attrib[k] = v
    self.children = []
    self.parent = None
    self.text = None
    self.tail = None
    self.tree = None

  def getroottree(self):
    el = self
    while el is not None:
      if el.tree is not None:
        return el.tree
      elif el.parent is None:
        return ElementTree(el)
      el = el.parent
    return None

  def getchildren(self):
    return self.children

  def getparent(self):
    return self.parent

  def getnext(self):
    if self.parent is None:
      return None
    i = self.parent.children.index(self)
    if i + 1 < len(self.parent.children):
      return self.parent.children[i + 1]
    return None

  def getprevious(self):
    if self.parent is None:
      return None
    i = self.parent.children.index(self)
    if i > 0:
      return self.parent.children[i - 1]
    return None

  def addnext(self, el):
    if self.parent is None:
      raise ValueError('No parent specified, thus no next item')
    i = self.parent.children.index(self)
    self.parent.insert(i+1, el)

  def addprevious(self, el):
    if self.parent is None:
      raise ValueError('No parent specified, thus no next item')
    i = self.parent.children.index(self)
    self.parent.insert(i, el)

  def find(self, tag):
    for el in self.children:
      if el.tag == tag:
        return el
    return None

  def findall(self, tag):
    return [el for el in self.children if el.tag == tag]

  def remove(self, el):
    i = self.children.index(el)
    self.__delitem__(i)

  def replace(self, el, el2):
    i = self.children.index(el)
    self.children[i].parent = None
    self.children[i] = el2
    el2.parent = self

  # Advanced iterators
  def iter(self, tag=None, *tags):
    return ElementDepthFirstIterator(self, tag=tag, inclusive=True, tags=tags)

  def iterchildren(self, tag=None, reversed=False, *tags):
    return ElementChildIterator(self, tag=tag, reversed=reversed, tags=tags)

  def itersiblings(self, tag=None, preceding=False, *tags):
    return SiblingsIterator(self, tag=tag, preceding=preceding, tags=tags)

  def iterancestors(self, tag=None, *tags):
    return AncestorsIterator(self, tag=tag, tags=tags)

  def iterdescendants(self, tag=None, *tags):
    return ElementDepthFirstIterator(self, tag=tag, inclusive=False, tags=tags)

  # Emulating dict for attributes
  def get(self, k, default=None):
    if k in self.attrib:
      return self.attrib[k]
    else:
      return default

  def set(self, k, v):
    self.attrib[k] = v

  def keys(self):
    return self.attrib.keys()

  def values(self):
    return self.attrib.values()

  def items(self):
    return self.attrib.items()

  # Emulating list for children
  def insert(self, idx, child):
    self.children.insert(idx, child)
    child.parent = self

  def append(self, child):
    self.children.append(child)
    child.parent = self

  def index(self, el):
    return self.children.index(el)

  def __getitem__(self, idx):
    return self.children.__getitem__(idx)

  def __delitem__(self, idx):
    self.children[idx].parent = None
    del self.children[idx]

  def __len__(self):
    return len(self.children)

  def __iter__(self):
    return self.children.__iter__()

  def next(self):
    return self.children.next()


class SubElement(Element):
  def __init__(self, parent, tag, attrib=None, **kwargs):
    Element.__init__(self, tag, attrib, **kwargs)
    parent.append(self)


def iselement(el):
  return isinstance(el, Element)

class XMLSyntaxError(Exception):
  pass


def _xml_decode(s):
  replacements = { 'quot': '"', 'apos': "'", 'amp': '&', 'lt': '<', 'gt': '>' }
  pos = s.find('&')
  while pos >= 0:
    semic = s.find(';', pos+1)
    repl = None
    if semic > pos + 1:
      entity = s[pos+1:semic]
      if entity in replacements:
        repl = replacements[entity]
      elif entity[0] == '#':
        try:
          ishex = entity[1] == 'x'
          code = int(entity[1+(1 if ishex else 0):], 16 if ishex else 10)
          if code < 128:
            repl = chr(code)
          # I have no idea how to make a unicode char out of a big integer
        except:
          pass
    if repl is not None:
      s = s[:pos] + repl + s[semic+1:]
    pos = s.find('&', semic+1)
  return s

def _parse_attributes(tag):
  """Parses string '<tag k="..." ...>' to an element."""
  pos = 1
  while tag[pos].isalnum() or tag[pos] in ('-', ':', '_', '.', '?'):
    pos += 1
  el = Element(tag[1:pos])
  while True:
    while pos < len(tag) and not tag[pos].isalnum() and tag[pos] not in ('/', '>'):
      pos += 1
    if pos == len(tag) or not tag[pos].isalnum():
      break
    eq = tag.find('=', pos)
    quote = tag[eq+1]
    qend = tag.find(quote, eq+2)
    el.set(tag[pos:eq], _xml_decode(tag[eq+2:qend]))
    pos = qend+1
  return el

def _read_element(s, pos):
  """Reads one element, returns tuple (element, pos_of_next_element)."""
  end = s.find('>', pos) + 1
  el = _parse_attributes(s[pos:end])
  if el is None:
    return (None, len(s))
  if s[end-2] != '/':
    # Non-empty tag
    nxt = s.find('<', end)
    if nxt > end:
      text = s[end:nxt].strip()
      if len(text):
        el.text = _xml_decode(text)
    while s[nxt+1] != '/':
      child, nxt = _read_element(s, nxt)
      el.append(child)
    if s[nxt+2:nxt+len(el.tag)+2] != el.tag:
      raise XMLSyntaxError('Unexpected closing tag: {0} instead of {1}'.format(s[nxt+2:nxt+len(el.tag)+2], el.tag))
    end = s.find('>', nxt+2) + 1
  pos = s.find('<', end)
  if pos > end:
    tail = s[end:pos].strip()
    if len(tail):
      el.tail = _xml_decode(tail)
  return (el, pos)

def fromstring(s):
  docinfo = DocInfo()
  root = None
  pos = s.find('<')
  while root is None and pos < len(s):
    if s[pos+1] == '?':
      end = s.find('?>', pos)
      decl = _parse_attributes(s[pos:end+1])
      docinfo.xml_version = decl.get('version', None)
      docinfo.encoding = decl.get('encoding', 'utf-8')
      pos = s.find('<', end + 2)
    elif s[pos+1] == '!':
      # Does not support internal DTD
      end = s.find('>', pos)
      sqbr = s.find('[', pos)
      if sqbr > 0 and sqbr < end:
        # Skip entities
        end = s.find('>', s.find(']', sqbr))
      docinfo.doctype = s[pos:end+1]
      sqbr = docinfo.doctype.find('[')
      if sqbr > 0:
        docinfo.doctype = docinfo.doctype[:sqbr].strip() + docinfo.doctype[docinfo.doctype.find(']', sqbr)+1:].strip()
      pos = s.find('<', end+1)
    else:
      root, pos = _read_element(s, pos)
      if root is None:
        break
  if root is not None:
    root.tree = ElementTree(root)
    root.tree.docinfo = docinfo
  return root

def XML(s):
  return fromstring(s)

def parse(f):
  root = fromstring(f.read())
  if root is None:
    return None
  return root.tree

def _xml_encode(s):
  return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

def tostring(el, pretty_print=False, with_tail=True, xml_declaration=False, encoding=None, prefix=''):
  result = ''
  if isinstance(el, ElementTree):
    if el.docinfo.xml_version is not None:
      if encoding is None:
        if el.docinfo.encoding is not None:
          encoding = el.docinfo.encoding
        else:
          encoding = 'utf-8'
      result += '<?xml version="{0}" encoding="{1}"?>\n'.format(el.docinfo.xml_version, _xml_encode(encoding))
    if el.docinfo.doctype is not None:
      result += el.docinfo.doctype + '\n'
    result += tostring(el.getroot(), pretty_print=pretty_print, with_tail=with_tail)
    return result

  if not len(prefix) and xml_declaration:
    if encoding is None:
      encoding = 'utf-8'
    result += '<?xml version="1.0" encoding="{0}"?>\n'.format(_xml_encode(encoding))
  if pretty_print:
    result += prefix
  result += '<' + el.tag
  for k, v in el.attrib.iteritems():
    result += ' {0}="{1}"'.format(k, _xml_encode(v))
  if len(el) == 0 and el.text is None:
    result += '/>'
    if pretty_print:
      result += '\n'
  else:
    result += '>'
    if pretty_print:
      result += '\n'
    sub_prefix = prefix + '  '
    if el.text is not None:
      if pretty_print:
        result += sub_prefix + el.text + '\n'
      else:
        result += el.text
    for child in el:
      result += tostring(child, pretty_print=pretty_print, with_tail=with_tail, prefix=sub_prefix)
    if pretty_print:
      result += prefix + '</' + el.tag + '>\n'
    else:
      result += '</' + el.tag + '>'
  if with_tail and el.tail is not None:
    if pretty_print:
      result += prefix + el.tail + '\n'
    else:
      result += el.tail
  if encoding is None or len(prefix):
    return result
  else:
    return result.encode(encoding)
