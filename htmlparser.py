from sys import stderr

# Errors
HTML_ERROR_UNKNOW               = 0x0
HTML_ERROR_SUCCESS              = 0x1
HTML_ERROR_START_NODE_EOF       = 0x2
HTML_ERROR_ROOT_NO_CLOSED       = 0x3
HTML_ERROR_ATTRS_EOF            = 0x4
HTML_ERROR_ATTR_EOF             = 0x5
HTML_ERROR_ATTR_KEY_EOF         = 0x6
HTML_ERROR_ATTR_AFTER_KEY_EOF   = 0x7
HTML_ERROR_ATTR_VALUE_EOF       = 0x8
HTML_ERROR_DIFF_CLOSE_NODE      = 0x9
HTML_ERROR_END_NODE_EOF         = 0xA
HTML_ERROR_COMMENT_EOF          = 0xB


EMPTY_TAGS = {
    "area",
    "base",
    "basefont",
    "br",
    "col",
    "frame",
    "hr",
    "img",
    "input",
    "isindex",
    "link",
    "meta",
    "param"
}

SCRIPT_TAGS = {
    "script",
    "style"
}


# Error messages
error2str = {
    HTML_ERROR_UNKNOW: 'unknow',
    HTML_ERROR_SUCCESS: 'no error'
}


def htmlErrorToStr(code, *args):
    if code in error2str:
        try:
            return error2str[code] % args
        except TypeError:
            return error2str[code] + "; with arguments: " + str(args)
    return error2str[HTML_ERROR_UNKNOW] + "; with code: " + str(code)


class HTMLParseError(object):
    def __init__(self, code=HTML_ERROR_UNKNOW, offset=None, args=()):
        self.error = htmlErrorToStr(code, *args)
        self.code = code
        self.line = None
        self.column = None
        self.offset = offset
        self.args = args
        self.linestr = ""
    
    def toString(self):
        if self.offset is None:
            return self.error
        return "offset %s, line %s, col %s : %s\ncontent: %s"%(self.offset, self.line, self.column, self.error, self.linestr)

    def print(self):
        print("Error: " + self.toString(), flush=True, file=stderr)
    
    def calcPos(self, txt):
        if self.offset is not None:
            i = 0
            line = 0
            lastlr = -1
            linestr = ""
            m = min(self.offset, len(txt))
            while i < m:
                c = txt[i]
                if c == '\n':
                    lastlr = i
                    line += 1
                    linestr = ""
                else:
                    linestr += c
                i += 1
            self.line = line
            self.column = self.offset - lastlr - 1
            self.linestr = linestr
        return self
    
    def __eq__(self, o) -> bool:
        return self.code == o.code
    
    def __ne__(self, o: object) -> bool:
        return self.code != o.code


HTML_SUCCESS = HTMLParseError(HTML_ERROR_SUCCESS)


# Element types
HTML_UNKNOW = 0x0
HTML_ROOT   = 0x1
HTML_NODE   = 0x2
HTML_TEXT   = 0x3


id_counter = 0
class HTMLElement(object):
    def __init__(self):
        self.type = HTML_UNKNOW
        global id_counter
        id_counter += 1
        self.id = id_counter
    
    def __eq__(self, o) -> bool:
        return self.id == o.id
    
    def __ne__(self, o: object) -> bool:
        return self.id != o.id


class HTMLRoot(HTMLElement):
    def __init__(self):
        super().__init__()
        self.childs = []
        self.innerText = ""
        self.type = HTML_ROOT
    
    def getFirstChild(self):
        if len(self.childs) > 0:
            return self.childs[0]
        return None

    def addChild(self, node):
        if node is not None and node != self:
            if node.type == HTML_TEXT:
                #print("Add child %i to %i: "%(node.id,self.id)+node.text)
                self.innerText += node.getText()
            elif node.type == HTML_NODE:
                pass#print("Add child %i to %i: "%(node.id,self.id)+node.typename)
            node.parent = self
            self.childs.append(node)
    
    def addChilds(self, nodes):
        for node in nodes:
            self.addChild(node)
    
    def strformat(self):
        output = ""
        i = 0
        while i < len(self.childs):
            if self.childs[i] != self:
                print("strformat() on %i from %i"%(self.childs[i].id,self.id))
                output += self.childs[i].strformat()
            i += 1
        return output
    
    def getChilds(self):
        return self.childs
    
    def getInnerText(self):
        return self.innerText

    def findByTag(self, typename, depth=-1):
        matched = []
        if depth == 0: return matched
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.getName() == typename:
                    matched.append(child)
                if depth != 1:
                    matched.extend(child.findByType(typename, depth-1))
        return matched
    
    def findFirstByTag(self, typename, depth=-1):
        if depth == 0: return None
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.getName() == typename:
                    return child
                if depth != 1:
                    r = child.findFirstByType(typename, depth-1)
                    if r is not None: return r
        return None

    def findByClass(self, classname, depth=-1):
        matched = []
        if depth == 0: return matched
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.hasClass(classname):
                    matched.append(child)
                if depth != 1:
                    matched.extend(child.findByClass(classname, depth-1))
        return matched
    
    def findFirstByClass(self, classname, depth=-1):
        if depth == 0: return None
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.hasClass(classname):
                    return child
                if depth != 1:
                    r = child.findFirstByClass(classname, depth-1)
                    if r is not None: return r
        return None
    
    def findById(self, idname, depth=-1):
        matched = []
        if depth == 0: return matched
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.getId() == idname:
                    matched.append(child)
                if depth != 1:
                    matched.extend(child.findById(idname, depth-1))
        return matched
    
    def findFirstById(self, idname, depth=-1):
        if depth == 0: return None
        for child in self.childs:
            if child.type == HTML_NODE:
                if child.getId() == idname:
                    return child
                if depth != 1:
                    r = child.findFirstById(idname, depth-1)
                    if r is not None: return r
        return None

    def findByAttrs(self, attrs, depth=-1):
        pass

    def find(self, typename, idname, classname, attrs, depth=-1):
        pass


class HTMLNode(HTMLRoot):
    def __init__(self, parent=None, childs=None):
        super().__init__()
        self.parent = parent
        self.childs = [] if childs is None else childs
        self.typename = ""
        self.attrs = {}
        self.type = HTML_NODE
        self.classes = set()
        self.attrid = None
    
    def getAttribute(self, attr):
        if attr in self.attrs:
            return self.attrs[attr]
        return None
    
    def setAttribute(self, attr, value=None):
        if attr in self.attrs:
            self.attrs[attr] = value
    
    def unsetAttribute(self, attr):
        if attr in self.attrs:
            del self.attrs[attr]
    
    def updateClasses(self):
        if 'class' in self.attrs:
            value = self.attrs['class']
            if value is not None:
                self.classes.clear()
                classes = value.split(' ')
                for classname in classes:
                    if classname:
                        self.classes.add(classname)
    
    def updateId(self):
        if 'id' in self.attrs:
            self.attrid = self.attrs['id']
    
    def strformatattrs(self):
        output = ""
        for k,v in self.attrs.items():
            output += " " + k
            if v is not None:
                output += '="' + str(v) + '"'
        return output
    
    def strformat(self):
        output = "<" + self.typename + self.strformatattrs()
        if self.typename in EMPTY_TAGS:
            output += "/>"
        else:
            output += ">"
            i = 0
            while i < len(self.childs):
                if self.childs[i] != self:
                    print("strformat() on %i from %i"%(self.childs[i].id,self.id))
                    output += self.childs[i].strformat()
                i += 1
            output += "</" + self.typename + ">"
        return output
    
    def getName(self):
        return self.typename
    
    def hasClass(self, classname):
        return classname in self.classes
    
    def getId(self):
        return self.attrid
    
    def getClasses(self):
        return self.classes


class HTMLText(HTMLElement):
    def __init__(self, text, parent=None):
        super().__init__()
        self.parent = parent
        self.text = text
        self.type = HTML_TEXT
    
    def strformat(self):
        return self.text
    
    def getText(self):
        return self.text


def _is_alphanumeric(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9'

def _is_alpha(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z'

def _is_space(c):
    return c == ' ' or c == '\r' or c =='\n' or c == '\t'

def _skip_space(i,m,txt):
    while i < m and _is_space(txt[i]): i += 1
    return i


# return: index, error, node, have_content
def _parse_startnode(i, m, txt):
    node = HTMLNode()

    if not _is_alpha(txt[i]):
        return i, HTML_SUCCESS, None, None

    while i < m:
        c = txt[i]
        if c == '>':
            return i + 1, HTML_SUCCESS, node, True
        elif c == '/' and txt[i+1] == '>':
            return i + 2, HTML_SUCCESS, node, False
        elif _is_space(c):
            i, err, have_content = _parse_attrs(i+1, m, txt, node)
            return i, err, node, have_content
        elif _is_alphanumeric(c):
            node.typename += c
        else:
            return i, HTML_SUCCESS, None, None # Ignore because it's not node start (ex: in script: "var x = a<b")
        i += 1
    
    return i, HTMLParseError(HTML_ERROR_START_NODE_EOF, i), None, False


# return: index, error, tag name
def _parse_endnode(i, m, txt):
    tagname = ""

    while i < m:
        c = txt[i]
        if c == '>':
            return i+1, HTML_SUCCESS, tagname
        elif _is_alpha(c):
            tagname += c
        else:
            return i, HTML_SUCCESS, None
        i += 1
    
    return i, HTMLParseError(HTML_ERROR_END_NODE_EOF, i), None


# return: index, error, have_content
def _parse_attrs(i, m, txt, node):
    while i < m:
        c = txt[i]
        if c == '>':
            return i+1, HTML_SUCCESS, True
        elif c == '/' and txt[i+1] == '>':
            return i+2, HTML_SUCCESS, False
        else:
            i, err, key, value, end, have_content = _parse_attr(i, m, txt)
            if err != HTML_SUCCESS:
                return i, err, have_content
            node.attrs[key] = value
            if end:
                return i, err, have_content
    return i, HTMLParseError(HTML_ERROR_ATTRS_EOF, i), False


def _parse_attr(i, m, txt):
    key = None
    value = None

    i = _skip_space(i, m, txt)
    if i >= m:
        return i, HTMLParseError(HTML_ERROR_ATTR_EOF, i), key, value, False, None

    i, err, key, have_value, end, have_content = _parse_attr_key(i, m, txt)
    if key is not None: key = key.lower()

    if err != HTML_SUCCESS:
        return i, err, key, value, end, have_content
    
    if end:
        return i, HTML_SUCCESS, key, value, end, have_content
    
    if have_value:
        i, err, value, end, have_content = _parse_attr_value(i, m, txt)
        if err != HTML_SUCCESS:
            return i, err, key, value, end, have_content

    return i, HTML_SUCCESS, key, value, end, have_content


# return: index, error, key, have_value, end, have_content
def _parse_attr_key(i, m, txt):
    key = ""

    while i < m:
        c = txt[i]
        if c == '>':
            return i+1, HTML_SUCCESS, key, False, True, True
        elif c == '/' and txt[i+1] == '>':
            return i+2, HTML_SUCCESS, key, False, True, False
        elif c == '=':
            return i+1, HTML_SUCCESS, key, True, False, None
        elif _is_space(c):
            i, err, have_value, end, have_content = _parse_attr_afterkey(i, m, txt)
            return i, err, key, have_value, end, have_content
        else:
            key += c
        i += 1

    return i, HTMLParseError(HTML_ERROR_ATTR_KEY_EOF, i), key, False, False, None


# return: index, error, have_value, end, have_content
def _parse_attr_afterkey(i, m, txt):
    i = _skip_space(i, m, txt)
    if i >= m:
        return i, HTMLParseError(HTML_ERROR_ATTR_AFTER_KEY_EOF, i), False, False, None

    c = txt[i]
    if c == '>':
        return i+1, HTML_SUCCESS, False, True, True
    elif c == '/' and txt[i+1] == '>':
        return i+2, HTML_SUCCESS, False, True, False
    elif c == '=':
        return i+1, HTML_SUCCESS, True, False, None
    return i, HTML_SUCCESS, False, False, None


# return: index, error, value, end, have_content
def _parse_attr_value(i, m, txt):
    i = _skip_space(i, m, txt)
    if i >= m:
        return i, HTMLParseError(HTML_ERROR_ATTR_VALUE_EOF, i), None, False, None

    c = txt[i]
    if c == '"' or c == "'":
        i, err, value = _parse_attr_value_quote(i+1, m, txt, c)
        return i, err, value, False, None
    else:
        return _parse_attr_value_noquote(i, m, txt)


# return: index, error, value
def _parse_attr_value_quote(i, m, txt, quote):
    value = ""
    escape_next = False
    while i < m:
        c = txt[i]
        if c == '\\':
            escape_next = True
        elif c == quote and escape_next == False:
            return i+1, HTML_SUCCESS, value
        else:
            value += c
            escape_next = False
        i += 1
    
    return i, HTMLParseError(HTML_ERROR_ATTR_VALUE_EOF, i), value


# return: index, error, value, end, have_content
def _parse_attr_value_noquote(i, m, txt):
    value = ""
    while i < m:
        c = txt[i]
        if c == '>':
            return i+1, HTML_SUCCESS, value, True, True
        elif c == '/' and txt[i+1] == '>':
            return i+2, HTML_SUCCESS, value, True, False
        elif _is_space(c):
            return i+1, HTML_SUCCESS, value, False, False
        else:
            value += c
        i += 1
    
    return i, HTMLParseError(HTML_ERROR_ATTR_VALUE_EOF, i), value, False, None


def _parse_text(i, m, txt):
    text = ""
    tmp = ""

    while i < m:
        c = txt[i]
        if c == '<':
            break
        elif _is_space(c):
            tmp += c
        else:
            if tmp:
                text += tmp + c
                tmp = ""
            else:
                text += c
        i += 1
    
    return i, HTML_SUCCESS, text


def _parse_comment(i, m, txt):
    comment = ""

    while i < m:
        c = txt[i]
        if c == '>':
            return i+1, HTML_SUCCESS, comment
        else:
            comment += c
        i += 1
    
    return i, HTMLParseError(HTML_ERROR_COMMENT_EOF, i), comment



class HTMLParser:
    def __init__(self, ignore_errors = True, quiet = False):
        self.root = HTMLRoot()
        self.quiet = quiet
        self.ignore_errors = ignore_errors

    def reset(self):
        self.root = HTMLRoot()
    
    def getroot(self):
        return self.root

    def format(self, node):
        return node.strformat()

    def parse(self, content):
        current = self.root
        i = 0
        m = len(content)
        content += '\0' # To avoid index out of range in some cases

        while i < m:
            c = content[i]
            
            if c == '<':
                if content[i+1] == '/':
                    i, err, tagname = _parse_endnode(i+2, m, content)

                    if err != HTML_SUCCESS:
                        return err.calcPos(content), self.root

                    if tagname is not None:
                        tagname = tagname.lower()

                        if tagname == current.typename:
                            current = current.parent

                        elif not (current.type == HTML_NODE and current.typename in SCRIPT_TAGS):
                            err = HTMLParseError(HTML_ERROR_DIFF_CLOSE_NODE, i).calcPos(content)
                            if not self.ignore_errors:
                                return err, self.root
                            if not self.quiet:
                                err.print()
                            # Try to fix error
                            if current.parent.type == HTML_NODE and tagname == current.parent.typename:
                                current = current.parent.parent


                # No comment or open tag inside scripting body
                elif not (current.type == HTML_NODE and current.typename in SCRIPT_TAGS):
                    if content[i+1] == '!':
                        i, err, comment = _parse_comment(i+2, m, content)

                        if err != HTML_SUCCESS:
                            return err.calcPos(content), self.root

                    else:
                        i, err, node, have_content = _parse_startnode(i+1, m, content)
                        if err != HTML_SUCCESS:
                            return err.calcPos(content), self.root

                        if node is not None:
                            node.typename = node.typename.lower()

                            if node.typename in EMPTY_TAGS:
                                have_content = False

                            node.updateClasses()
                            node.updateId()

                            current.addChild(node)
                            if have_content:
                                current = node
                
                else:
                    i += 1
            
            elif not _is_space(c):
                i, err, txt = _parse_text(i, m, content)

                if err != HTML_SUCCESS:
                    return err.calcPos(content), self.root
                
                current.addChild( HTMLText(txt) )
            
            else:
                i += 1

        if current != self.root:
            err = HTMLParseError(HTML_ERROR_ROOT_NO_CLOSED)
            if not self.ignore_errors:
                return err, self.root
            if not self.quiet:
                err.print()
        
        return HTML_SUCCESS, self.root



# Test code
'''
parser = HTMLParser()

err, parsed = parser.parse("""
<html>
    <head>
        <title>Test</title>
        <meta test="blabla"/>
    </head>
    <body>
        <a href="#"><h1>Big Title</h1></a>
    </body>
</html>
""")

err, parsed = parser.parse("""
<div class="col search_capsule">
    <img test abcd=cool src="https://cdn.akamai.steamstatic.com/steam/apps/1022310/capsule_sm_120.jpg?t=1622770274" srcset="https://cdn.akamai.steamstatic.com/steam/apps/1022310/capsule_sm_120.jpg?t=1622770274 1x, https://cdn.akamai.steamstatic.com/steam/apps/1022310/capsule_231x87.jpg?t=1622770274 2x">
</div>
""")

if err == HTML_SUCCESS:
    print(parsed.strformat())
else:
    err.print()
'''