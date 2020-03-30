#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 21:49:54 2017

@author: eendebakpt
"""

#%%
#from xml.etree import cElementTree as ET
from collections import defaultdict

import xml.etree as xmletree
import lxml.etree as lxmletree

import lxml.etree as etree
from lxml.etree import ElementTree
from lxml import etree as ET
xmlElement = ET.Element
SubElement = etree.SubElement

from xml.dom import minidom
import json
from collections import OrderedDict

#%%

def xml_float(line, tag, namespace, default=0):
    """ Get float value from etree element """
    try:
        val = float(line.find(namespace + tag).text)
    except:
        val = default
    return val

def xml_int(line, tag, namespace, default=0):
    """ Get float value from etree element """
    try:
        val = int(line.find(namespace + tag).text)
    except:
        val = default
    return val

def xml_boolean(line, tag, namespace, default=False):
    """ Get bool value from etree element """
    try:
        val = (line.find(namespace + tag).text)
    except:
        val = default
        
    if val=='false' or val=='0' or val=='False' or val==False or val==None:
        val=False
    else:
        val=True
    return val


def xml_string(line, tag, namespace, default=None):
    """ Get string value from etree element """
    try:
        val = (line.find(namespace + tag).text)
    except:
        val = default
    return val

def set_xml_string(xmlelem, tag, value, namespace='', default=None):
    """ Set string value from etree element """
    xx = (xmlelem.find(namespace + tag))
    if xx is None:
        print('could not set tag %s' % tag)
        return
    xx.text = str(value)


#%%
try:
    basestring
except NameError:  # python3
    basestring = str


def prettifyXML(xmls : str):
    """ Reformat XML data string """
    x = lxml.etree.fromstring(xmls)
    x = lxml.etree.tostring(x, pretty_print=True)
    return x


def prettifyXMLelem(elem):
    """Return a pretty-printed XML string for the Element.
    
    Args:
        elem (xml element)
    Returns:
        xml (str) : prettyfied xml
    """
    rough_string = xmletree.ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def typemap(t):
    """ Convert type to string describing the type """
    if isinstance(t, int):
        return 'int'
    elif isinstance(t, float):
        return 'float'
    elif t is None:
        return 'none'
    elif isinstance(t, np.ndarray):
        return 'array'
    elif isinstance(t, basestring):
        return 'str'
    elif isinstance(t, list):
        return 'list'
    else:
        return str


def typecast(t, value):
    """ Cast a string value to specified type """
    if t == 'int':
        return int(value)
    elif t == 'float':
        return float(value)
    elif t == 'none':
        return None
    elif t == 'str':
        return basestring(value)
    elif t == 'list':
        return basestring(value)
    elif t == 'array':
        q = np.array(json.loads(value)).astype(np.float32)
        #c = np.fromstring(c, dtype=int, sep=',')
        return q
    elif t == None:
        return value
    else:
        return str


def etree_to_dict(t, verbose=0):
    """ Convert etree structure to dict """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        if verbose:
            print('%d childeren:' % len(children))
        for dc in map(etree_to_dict, children):
            # print(dc)
            for k, v in dc.items():
                if verbose:
                    print('  child %s' % k)
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    etype = None
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        # print(d)
        if '@type' in d[t.tag]:
            etype = d[t.tag]['@type']
            if verbose:
                print('element %s: found type attribute %s' % (t, etype))
    if verbose:
        print('etree_to_dict: t: %s' % t)
#    if t.type:
#        print('element %s: type %s'  % (t.text, t.type))
    if t.text:
        text = t.text.strip()
        if etype is not None:
            if children:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = typecast(etype, text)
        else:
            if children or t.attrib:
                if text:
                    d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
    return d


def dict_to_etree(d):
    def _to_etree(d, root):
        if d is False:
            pass
        elif isinstance(d, basestring):
            root.text = d
        elif isinstance(d, list):
            root.text = dict_to_etree(d)
            root.set('type', typemap(d))
        elif isinstance(d, np.ndarray):
            root.text = str(d.tolist())
            root.set('type', typemap(d))
            #root.set('dtype', d.dtype )
            #root.set('shape', d.shape )

        elif isinstance(d, (int, float)):
            root.text = str(d)
            root.set('type', typemap(d))
        elif d is None:
            root.text = str(d)
            root.set('type', typemap(d))
        elif isinstance(d, dict):
            for k, v in sorted(d.items()):
                assert isinstance(k, basestring)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, basestring)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, basestring)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            assert d == 'invalid type', (type(d), d)
    assert isinstance(d, dict)  # and len(d) == 1
    tag, body = next(iter(d.items()))
    node = xmlElement(tag)
    _to_etree(body, node)
    return node


def dict_to_xml(d):
    """ Convert dict to XML string """
    #xmls = dicttoxml.dicttoxml(d)
    #x = etree.parse(xmls)#
    xmls = (etree.tostring(dict_to_etree(d)))
    x = etree.fromstring(xmls)
    x = etree.tostring(x, pretty_print=True, xml_declaration=True)
    return x


def xml_to_dict(xml, verbose=0):
    """ Convert XML string to dict """
    if isinstance(xml, basestring):
        xml = xml.encode('ASCII')
    root = etree.fromstring(xml)
    d = etree_to_dict(root, verbose=verbose)
    # d=xmltodict.parse(xml)
    return d


def write_xml(d, filename, root_tag='horse'):
    """ Write dictionary to XML file """
    dh = OrderedDict({root_tag: d})
    with open(filename, 'wt') as fid:
        fid.write(dict_to_xml(dh).decode('ASCII'))


def read_xml(filename, xmlstring=None, root_tag='horse'):
    if filename is None:
        s = xmlstring
    else:
        with open(filename, 'rt') as fid:
            s = fid.read()

    d = xml_to_dict(s)
    if root_tag is not None:
        assert root_tag in d
        return d[root_tag]
    else:
        return d

import re
def get_namespace(element):
  """ Return namespace from elementtree element """
  try:
      m = re.match(r'\{.*\}', element.tag)
      return m.group(0) if m else ''
  except TypeError:
      # could be we are looking at a comment element
      return None

def show_xml_elem(elem, pad='', r=0, maxsub=5):
    """ Print an XML element 
    
    Args:
        elem (list of xml elements or single xml element)
        pad (str): padding before printing
        r (int): recursion depth
        maxsub: maximum number of elements to display at each level
    """
    if isinstance(elem, str):
        tree = etree.parse(elem)
        root = tree.getroot()
        elem = root
    if isinstance(elem, list):
        lst=elem
    else:
        ns=get_namespace(elem)
        tag = elem.tag
        if tag.startswith(ns):
            tag=tag[len(ns):]
        ww='%s%s: %s' % (pad,tag, elem.text)
        print(ww)
        lst = elem.getchildren()
    if r>4:
        return
    pad += '  '
    for jj, v in enumerate(lst):
        if jj<=maxsub:
            show_xml_elem(v, pad, r=r+1)
        else:
            print('%s...' % pad)
            break
  
def xml_strip_tags(root, tags=[], verbose=0, namespace=''):
    """ Strips elements from xml tree """
    lines = root.getchildren()
    for linenum, line in enumerate(lines):
        inputType = xml_string(line, 'Type', namespace, default=None)
        if inputType in tags:
            root.remove(line)
            if verbose:
                print(' xml_strip_tags: strip element %d with tag %s' %
                      (linenum, inputType))
                
if __name__ == '__main__':
    import pdb
    import horsetno
    from horsetno.pgeometry import show_dictionary

    d = {'horse': {'generated': horsetno.datestring(), 'data': {'mystring': 'myfile', 'float': 0.2, 'np': np.array([1, 2]), 'subdict': {'a': 'a', 'b': 2}, 'intlist': [1, 2, 3, 4]}}}
    ss = dict_to_xml(d)
    print('dict to string:\n %s' % ss.decode('ASCII'))
    d = xml_to_dict(ss)
    print('xml to dict: \n%s' % d)
    show_dictionary(d, show_values=True)

#%%
