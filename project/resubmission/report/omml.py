"""A small builder for native Word equations (OMML), in the style of Project_report_group6.docx:
Cambria Math, italic letters, upright names. Each function returns an XML fragment as a string.

    para = display(sub('x', 'k+1'), r('='), r('F'), d(sub('x', 'k') + r(',') + sub('u', 'k')))
"""

from xml.sax.saxutils import escape

M_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
FONT = '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
CTRL = '<m:ctrlPr>%s</m:ctrlPr>' % FONT


def r(text):
    """Italic math run (letters), as Word types them."""
    return '<m:r>%s<m:t xml:space="preserve">%s</m:t></m:r>' % (FONT, escape(text))


def rp(text):
    """Upright run: function names, units, words."""
    return '<m:r><m:rPr><m:sty m:val="p"/></m:rPr>%s<m:t xml:space="preserve">%s</m:t></m:r>' % (FONT, escape(text))


def _e(x):
    return x if x.startswith('<') else r(x)


def sub(base, s):
    return '<m:sSub><m:sSubPr>%s</m:sSubPr><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (CTRL, _e(base), _e(s))


def sup(base, s):
    return '<m:sSup><m:sSupPr>%s</m:sSupPr><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>' % (CTRL, _e(base), _e(s))


def subsup(base, s, p):
    return ('<m:sSubSup><m:sSubSupPr>%s</m:sSubSupPr><m:e>%s</m:e><m:sub>%s</m:sub><m:sup>%s</m:sup></m:sSubSup>'
            % (CTRL, _e(base), _e(s), _e(p)))


def frac(num, den):
    return '<m:f><m:fPr>%s</m:fPr><m:num>%s</m:num><m:den>%s</m:den></m:f>' % (CTRL, _e(num), _e(den))


def d(inner, beg='(', end=')'):
    return ('<m:d><m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/>%s</m:dPr><m:e>%s</m:e></m:d>'
            % (escape(beg), escape(end), CTRL, _e(inner)))


def norm2(inner):
    """||inner||^2"""
    return sup(d(inner, '‖', '‖'), '2')


def nary(op, lo, hi, body):
    hide = '' if hi else '<m:supHide m:val="1"/>'
    return ('<m:nary><m:naryPr><m:chr m:val="%s"/><m:limLoc m:val="undOvr"/>%s%s</m:naryPr>'
            '<m:sub>%s</m:sub><m:sup>%s</m:sup><m:e>%s</m:e></m:nary>'
            % (op, hide, CTRL, _e(lo), _e(hi) if hi else '', _e(body)))


def summ(lo, hi, body):
    return nary('∑', lo, hi, body)


def dot(x):
    return '<m:acc><m:accPr><m:chr m:val="˙"/>%s</m:accPr><m:e>%s</m:e></m:acc>' % (CTRL, _e(x))


def hat(x):
    return '<m:acc><m:accPr><m:chr m:val="̂"/>%s</m:accPr><m:e>%s</m:e></m:acc>' % (CTRL, _e(x))


def limlow(name, lim):
    return ('<m:limLow><m:limLowPr>%s</m:limLowPr><m:e>%s</m:e><m:lim>%s</m:lim></m:limLow>'
            % (CTRL, rp(name), _e(lim)))


def func(name, arg):
    return '<m:func><m:funcPr>%s</m:funcPr><m:fName>%s</m:fName><m:e>%s</m:e></m:func>' % (CTRL, rp(name), _e(arg))


def eqarr(rows):
    return '<m:eqArr><m:eqArrPr>%s</m:eqArrPr>%s</m:eqArr>' % (CTRL, ''.join('<m:e>%s</m:e>' % x for x in rows))


def math(*parts):
    """One display equation, as the content of a centred paragraph."""
    return ('<m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr><m:oMath>%s</m:oMath></m:oMathPara>'
            % ''.join(_e(p) for p in parts))
