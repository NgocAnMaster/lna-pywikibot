#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Copyright (C) 2012 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""


"""
helper functions for indexer2.py
"""
#from __future__ import unicode_literals
import sys
import re
import urllib
import difflib
import time
import calendar
import datetime
import pywikibot
import ArchiveIndexer2 #for error classes
from pywikibot import textlib
SITE = pywikibot.Site()
LOG_TEXT = ''
MONTH_NAMES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')
MONTH_REGEX = '|'.join(month for month in MONTH_NAMES)



def parseInstructions(page):
    """
    Parses the index template for all of the parameters
    """
    text = page.get()
    #print u'Parsing instructions for [[%s]].' % page.title()
    key = text.find('{{Thành viên:AnsterBot/ArchiveIndex/IndexConfig')
    data = text[key:].split('}}')[0][36:] #kinda scared about hardcoding so much
    #remove any comments (apparently users do this)
    cleaned = textlib.removeDisabledParts(data)
    info = {}
    info['mask'] = []
    info['talkpage'] = page.title()
    for param in cleaned.split('|'):
        param = clean(param)
        if param.startswith('target='):
            target = clean(param[7:])
            if target.startswith('/'):
                target = page.title() + target
            elif target.startswith('./'):
                target = page.title() + target[1:]
            info['target'] = target
        elif param.startswith('mask='):
            mask = clean(param[5:])
            if mask.startswith('/'):
                mask = page.title() + mask
            elif mask.startswith('./'):
                mask = page.title() + mask[1:]
            info['mask'].append(mask)
        elif param.startswith('indexhere='):
            value = param[10:]
            if clean(value.lower()) == 'yes':
                info['indexhere'] = True
            else:
                info['indexhere'] = False
        elif param.startswith('template='):
            info['template'] = clean(param[9:].replace('\n',''))
        elif param.startswith('leading_zeros='):
            try:
                info['leading_zeros'] = int(clean(param[14:]))
            except ValueError:
                pass
        elif param.startswith('first_archive='):
            info['first_archive'] = clean(param[14:])
    #set default values if not already set
    for key in info.keys():
        if type(info[key]) == type(u''):
            if info[key].isspace() or (not info[key]):
                del info[key]
    
    if 'leading_zeros' not in info:
        info['leading_zeros'] = 0
    if 'indexhere' not in info:
        info['indexhere'] = False
    if 'template' not in info:
        info['template'] = 'Thành viên:AnsterBot/ArchiveIndex/defaulttemplate'
    if info['template'] == 'template location':
        info['template'] = 'Thành viên:AnsterBot/ArchiveIndex/defaulttemplate'
    return info
def clean(text):
    """various cleaning functions to simplify parsing bad text"""
    
    #first lets eliminate any useless whitespace
    text = text.strip()
    # clean up when people do |indehere=<yes>
    search = re.search('(.*?)=\<(#|yes|no|month|year|.*?)\>', text)
    if search:
        front = search.group(1) + '='
        if search.group(2) in ['#', 'month', 'year']:
            pass
        elif search.group(2) in ['yes', 'no'] :
            text = search.group(2)
        else:
            text = search.group(2)
        text = front + text
    #remove wikilinks from everything
    search = re.search('\[\[(.*?)\]\]', text)
    if search:
        text = text.replace(search.group(0), search.group(1))
    return text

def __prefixNumber(num, leading):
    """
    Prefixes "num" with %leading zeroes.
    """
    length = int(leading)+1
    num = str(num)
    while len(num) < length:
        num = '0' + num
    return num

def __nextMonth(month, year):
    """
    Returns what the next month should be
    If December --> January, then it ups the year as well
    """
    
    index = MONTH_NAMES.index(month)
    if index == 11:
        new_index = 0
        year += 1
    else:
        new_index = index + 1
    new_month = MONTH_NAMES[new_index]
    return new_month, year


def getNextMask(current, pattern, leading_zeroes=0):
    if '<#>' in pattern:
        regex = pattern.replace('<#>', '(\d+)')
        key = int(re.search(regex, current).group(1))
        archive_num = __prefixNumber(key+1, leading_zeroes)
        return pattern.replace('<#>', archive_num)
    if '<month>' in pattern:
        regex = pattern.replace('<month>', '(%s)' % MONTH_REGEX).replace('<year>', '(\d\d\d\d)')
        match = re.search(regex, current)
        month, year = __nextMonth(match.group(1), int(match.group(2)))
        return pattern.replace('<month>', month).replace('<year>', str(year))
        
        
        
        
        
def getMasks(info):
    data = list()
    for mask in info['mask']:
        if '<#>' in mask:
            key = 1
            keep_going = True
            #numerical archive
            while keep_going:
                archive_num = __prefixNumber(key, info['leading_zeros'])
                title = mask.replace('<#>', archive_num)
                page = pywikibot.Page(SITE, title)
                key += 1
                if page.exists():
                    data.append(page)
                else:
                    keep_going = False
                        
        elif '<month>' in mask:
            if 'first_archive' not in info:
                raise ArchiveIndexer2.NoMask
            #grab the month and year out of the first archive
            regex = mask.replace('<month>', '(%s)' % MONTH_REGEX).replace('<year>', '(\d\d\d\d)')
            match = re.search(regex, info['first_archive'])
            month = match.group(1)
            year = int(match.group(2))
            keep_going = True
            while keep_going:
                title = mask.replace('<month>', month).replace('<year>', str(year))
                page = pywikibot.Page(SITE, title)
                if page.exists():
                    data.append(page)
                    month, year = __nextMonth(month, year)
                else:
                    keep_going = False
        elif '<year>' in mask: #special case for when only a year is provided
            if 'first_archive' not in info:
                raise ArchiveIndexer2.NoMask
            regex = mask.replace('<year>', '(\d\d\d\d)')
            match = re.search(regex, info['first_archive'])
            year = int(match.group(1))
            keep_going = True
            while keep_going:
                title = mask.replace('<year>', str(year))
                page = pywikibot.Page(SITE, title)
                if page.exists():
                    data.append(page)
                    year += 1
                else:
                    keep_going = False
        else: #assume the mask is the page
            if ('<' in mask) or ('>' in mask):
                print (u'ERRORERROR: Did not parse %s properly.' % mask)
                #continue
            page = pywikibot.Page(SITE, mask)
            if page.exists():
                data.append(page)
    if info['indexhere']:
        data.append(pywikibot.Page(SITE, info['talkpage']))
    return data



def followInstructions(info):
    #verify all required parameters are there
    if 'mask' not in info or 'target' not in info:
        return '* [[:%s]] có bản mẫu thiết lập sai.' % info['talkpage']
    #verify we can edit the target, otherwise just skip it
    #hopefully this will save processing time
    indexPage = pywikibot.Page(SITE, info['target'])
    talkPage = pywikibot.Page(SITE, info['talkpage'])
    try:
        indexPageOldText = indexPage.get()
    except pywikibot.exceptions.IsRedirectPage:
        indexPage = indexPage.getRedirectTarget()
        indexPageOldText = indexPage.get()
    except pywikibot.exceptions.NoPage:
        return '* [[:%s]] không có chuỗi an toàn.' % info['talkpage']
    if not __okToEdit(indexPageOldText):
        return '* [[:%s]] không có chuỗi an toàn.' % info['talkpage']
    edittime = pywikibot.Timestamp.fromISOformat(indexPage.editTime())
    twelvehr = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    if twelvehr < edittime:
        print (u'Edited %s less than 12 hours ago.' % indexPage.title())
        #return
    #looks good, lets go
    data = {}
    #first process the mask
    masks = getMasks(info)
    data['archives'] = masks
    #finished the mask processing!
    #now verify the template exists
    template = pywikibot.Page(SITE, info['template'])
    if not template.exists():
        #fallback on the default template
        template = pywikibot.Page(SITE, 'Thành viên:AnsterBot/ArchiveIndex/defaulttemplate')
    data['template'] = template.get()
    #finished the template part    
    #lets parse all of the archives now
    data['parsed'] = list()
    for page in data['archives']:
        parsed = parseArchive(page)
        data['parsed'].extend(parsed)
    #build the index      
    indexText = __buildIndex(data['parsed'], data['template'], info)
    print (u'>>>Will edit %s' % indexPage.title())
    #pywikibot.showDiff(indexPageOldText, indexText)
    if __verifyUpdate(indexPageOldText, indexText):
        indexPage.put_async(indexText, 'BOT: Cập nhật mục lục')
        return '* Ghi mục lục của [[%s]] đến [[%s]] thành công.\n' % (talkPage.title(), indexPage.title())
    else:
        return '* [[%s]] không cần phải cập nhật mới.\n' % talkPage.title()

def __okToEdit(text):
    return bool(re.search('<!-- AnsterBot can edit it -->', text))


def __buildIndex(parsedData, template, info):
    """
    Reads the template and creates the index for it
    """
    #first lets read the template
    #print u'Building the index.' 
    templateData = {}
    key = template.find('<nowiki>')
    lastKey = template.find('</nowiki>')
    if key == -1:
        key = template.find('<pre>')
        lastKey = template.find('</pre>')
    importantStuff = template[key+8:lastKey]
    split = re.split('<!--\s', importantStuff)
    for item in split:
        if item.startswith('HEADER'):
            templateData['header'] = item[11:]
        elif item.startswith('ROW'):
            templateData['row'] = item[8:]
        elif item.startswith('ALT ROW'):
            templateData['altrow'] = item[12:]
        elif item.startswith('FOOTER'):
            templateData['footer'] = item[11:]
        elif item.startswith('END'):
            templateData['end'] = item[8:]
        elif item.startswith('LEAD'):
            templateData['lead'] = item[9:]
    if 'altrow' not in templateData:
        templateData['altrow'] = templateData['row']
    if 'lead' not in templateData:
        templateData['lead'] = ''
    if 'end' not in templateData:
        templateData['end'] = ''
    #print templateData
    #finished reading the template
    indexText = '<!-- AnsterBot can edit it -->'
    indexText += templateData['lead']
    reportInfo = 'Báo cáo được tạo theo yêu cầu từ [[%s]]. Nó trùng với tiền tố sau: ' % pywikibot.Page(SITE, info['talkpage']).title()
    reportInfo += ' ,'.join([m.strip() for m in info['mask']])
    reportInfo += '\n<br />\nNó được tạo vào lúc ~~~~~ bởi [[Thành viên:AnsterBot|AnsterBot]].\n'
    indexText += reportInfo
    indexText += templateData['header']
    alt = False
    for item in parsedData:
        if alt:
            rowText = templateData['altrow']
            alt = False
        else:
            rowText = templateData['row']
            alt = True
        rowText = rowText.replace('%%topic%%', item['topic'])
        rowText = rowText.replace('%%replies%%', str(item['replies']))
        rowText = rowText.replace('%%link%%', item['link'])
        rowText = rowText.replace('%%first%%', item['first'])
        rowText = rowText.replace('%%firstepoch%%', str(item['firstepoch']))
        rowText = rowText.replace('%%last%%', item['last'])
        rowText = rowText.replace('%%lastepoch%%', str(item['lastepoch']))
        rowText = rowText.replace('%%duration%%', item['duration'])
        rowText = rowText.replace('%%durationsecs%%', str(item['durationsecs']))
        indexText += rowText
    indexText += templateData['footer']
    indexText += templateData['end']
    return indexText


def parseArchive(page):
    """
    Parses each individual archive
    Returns a list of dicts of the following info:
        topic - The heading
        replies - estimated count (simply finds how many instances of "(UTC)" are present
        link - link to that section
        first - first comment
        firstepoch - first comment (epoch)
        last - last comment
        lastepoch - last comment (epoch)
        duration - last-first (human readable)
        durationsecs - last-first (seconds)
    
    """
    tmp_page = page
    while tmp_page.isRedirectPage():
        tmp_page = tmp_page.getRedirectTarget()
    text = tmp_page.get()
    print (u'Parsing %s.' % page.title())
    threads = splitIntoThreads(text)
    data = list()
    for thread in threads:
        d = {}
        d['topic'] = thread['topic'].strip()
        d['link'] = '[[%s#%s]]' % (page.title(), __cleanLinks(d['topic']))
        content = thread['content']
        d['content'] = content
        #hackish way of finding replies
        found = re.findall('\(UTC\)', content)
        d['replies'] = len(found)
        #find all the timestamps
        ts = re.finditer('(\d\d:\d\d|\d\d:\d\d:\d\d), ngày (\d\d) tháng (%s) năm (\d\d\d\d)' % (MONTH_REGEX, content))
        epochs = list()
        for stamp in ts:
            mw = stamp.group(0)
            parsed = mwToEpoch(mw)
            if parsed:
                epochs.append(calendar.timegm(parsed))
        earliest = 999999999999999999
        last = 0
        for item in epochs:
            if item < earliest:
                earliest = item
            if item > last:
                last = item
        if earliest == 999999999999999999:
            earliest = 'Unknown'
            d['duration'] = 'Unknown'
            d['durationsecs'] = 'Unknown'
        if last == 0:
            last = 'Unknown'
            d['duration'] = 'Unknown'
            d['durationsecs'] = 'Unknown'
            
        d['first'] = epochToMW(earliest)
        d['firstepoch'] = earliest
        d['last'] = epochToMW(last)
        d['lastepoch'] = last
        if not d.has_key('duration'):
            d['duration'] = humanReadable(last - earliest)
            d['durationsecs'] = last - earliest
        data.append(d)
    return data

def splitIntoThreads(text, level3=False):
    """
    Inspired/Copied by/from pywikipedia/archivebot.py
    """
    if level3:
        regex = '^=== *([^=].*?) *=== *$'
    else:
        regex = '^== *([^=].*?) *== *$'
    lines = text.split('\n')
    found = False
    threads = list()
    curThread = {}
    for line in lines:
        threadHeader = re.search(regex,line)
        if threadHeader:
            found = True
            if curThread:
                threads.append(curThread)
                curThread = {}
            curThread['topic'] = threadHeader.group(1)
            curThread['content'] = ''
        else:
            if found:
                curThread['content'] += line + '\n'
    if curThread:
        threads.append(curThread)
    if not threads and not level3:
        threads = splitIntoThreads(text, level3=True)
    return threads

def __cleanLinks(link):
    link = link.encode('utf-8')
    #[[piped|links]] --> links
    search = re.search('\[\[:?(.*?)\|(.*?)\]\]', link)
    while search:
        link = link.replace(search.group(0), search.group(2))
        search = re.search('\[\[:?(.*?)\|(.*?)\]\]', link)
    #[[wikilinks]] --> wikilinks
    search = re.search('\[\[:?(.*?)\]\]', link)
    while search:
        link = link.replace(search.group(0), search.group(1))
        search = re.search('\[\[:?(.*?)\]\]', link)
    #'''bold''' --> bold
    #''italics'' --> italics
    search = re.search("('''|'')(.*?)('''|'')", link)
    while search:
        link = link.replace(search.group(0), search.group(2))
        search = re.search("('''|'')(.*?)('''|'')", link)
    #<nowiki>blah</nowiki> --> blah
    link = link.replace('<nowiki>','').replace('</nowiki>','')
    link = urllib.quote(link)
    return link


def epochToMW(timestamp):
    """
    Converts a unix epoch time to a mediawiki timestamp
    """
    if type(timestamp) == type(''):
        return timestamp
    struct = time.gmtime(timestamp)
    return time.strftime('%H:%M, ngày %d tháng %B năm %Y', struct)
    
def mwToEpoch(timestamp):
    """
    Converts a mediawiki timestamp to unix epoch time
    """
    try:
        return time.strptime(timestamp, '%H:%M, ngày %d tháng %B năm %Y')
    except ValueError:
        try:
            return time.strptime(timestamp, '%H:%M:%S, ngày %d tháng %B năm %Y') # Some users (ex: Pathoschild) include seconds in their signature
        except ValueError:
            return None #srsly wtf?


def humanReadable(seconds):
    return str(datetime.timedelta(seconds=seconds))


def __verifyUpdate(old, new):
    """
    Verifies than an update is needed, and we won't be just updating the timestamp
    """
    old2 = re.sub('được tạo vào lúc (.*?) bởi', 'được tạo vào lúc ~~~~~ bởi', old)
    #pywikibot.showDiff(old2, new)
    update = False
    for line in difflib.ndiff(old2.splitlines(), new.splitlines()):
        if not line.startswith(' '):
            if line.startswith('+'):
                if not line[1:].isspace():
                    update = True
                    break
            elif line.startswith('-'):
                if not line[1:].isspace():
                    update = True
                    break
    return update

