import sys, getopt
import pywikibot

from pywikibot.pagegenerators import * # pagegenerators: tìm kiếm danh sách trang
from pywikibot.config import * # config: cấu hình bot (user, password,...)
#from pywikibot.login import *

import re # gói regex dành cho các biểu thức chính quy
import time


# -- helpers -------------------------------------------------- #
# ------------------------------------------------------------- #

def replace_all(text, dict):
    """
        thay thế toàn bộ văn bản theo từ điển
            text: văn bản gốc - string
            dict: từ điển - object
            return: văn bản đã được thay thế - string
    """

    for i, j in dict.iteritems():
        text = text.replace(i, j)
    return text

def strip_all(text, list):
    """
        tỉa văn bản đầu cuối theo danh sách
            text: văn bản gốc - string
            list: danh sách cần tỉa - list
            return: văn bản đã được thay thế - string
    """

    loop = 0
    while True:
        loop += 1
        if (loop > 50): break

        for i in list:
            text = text.strip(i)

        count = 0
        for i in list:
            if (len(text) >= len(i)):
                if (i in text[0:len(i) + 1] or i in text[-len(i):]):
                    count = count + 1
                    break
        if (count == 0): break
      
    return text


def hide_by_string1(text, start, end):
    """
        ẩn văn bản theo cặp thẻ chỉ định
            text: văn bản gốc - string
            start: chuỗi bắt đầu - string
            end: chuỗi kết thúc - string
            return: trả về văn bản đã được thay đổi - string
    """

    hide_text = ''
    flag = False

    for i, c in enumerate(text):
        try:
            if (text[i] == start):
                hide_text += start
                flag = True
        except: pass

        try:
            if (text[i] == end):
                flag = False
        except: pass

        if (flag == True): hide_text += '#'
        else: hide_text += c

    return hide_text
              

def hide_by_string2(text, start1, start2, end1, end2):

    """
        ẩn văn bản theo cặp thẻ chỉ định
            text: văn bản gốc - string
            start1, start2: chuỗi bắt đầu - string
            end1, end2: chuỗi kết thúc - string
            return: trả về văn bản đã được thay đổi - string
    """

    hide_text = ''
    flag = False
     
    for i, c in enumerate(text):
        try:
            if (text[i] == start1 and text[i+1] == start2):
                hide_text += start1 + start2
                flag = True
        except: pass

        try: 
            if (text[i] == end1 and text[i+1] == end2):
                flag = False
        except: pass

        if (flag == True): hide_text += '#'
        else: hide_text += c

    return hide_text
              

def hide_code(text):

    hide_text = hide_by_string2(text, '{', '{', '}', '}') # hide templates
    hide_text = hide_by_string1(hide_text, '<', '>') # hide code chunks

    # split text + remove special characters
    chunks = [strip_all(t, ['\n', '<', '>', '{{', '}}', '*']).strip() for t in hide_text.split('#') if strip_all(t, ['\n', '<', '>', '{{', '}}', '*']).strip() != '']

    # remove some prefixes
    prefixes = ['Tập tin:', 'File:', 'Thể loại:', 'Category:']
    chunks = [c for c in chunks if len([p for p in prefixes if p in c]) == 0]
    chunks = [c for c in chunks if len(c.split()) > 10] # not use too short chunks
     
    #print('text_chunk: ', chunks)
    return chunks

# --- wiki ---------------------------------------------------- #
# ------------------------------------------------------------- #

def check_redirect(text):
    """
        kiểm tra redirect trong nội dung văn bản (thường có cú pháp #redirect hoặc #đổi)
        bot không chạy ở các trang redirect
            text: văn bản - string
            return: boolean
    """

    texts = text.split('\n')
    if (len(texts) < 1): return False

    check1 = re.search(r'#\s*[Đđ][ổỔ][iI]\s*', texts[0])
    check2 = re.search(r'#\s*[Rr][Ee][Dd][Ii][Rr][Ee][Cc][Tt][Ss]\s*', texts[0])

    if check1: return True
    if check2: return True

    return False
    
def punctuation_fixes(title, text, summary):
    """
        ***HÀM ĐANG BỊ LỖI
        sửa khoảng trắng dư trước dấu câu
            title: tên trang - string
            text: nội dung trang - string
            summary: nội dung tóm tắt - string
            return: trả về các biến trên
    """

    new_text = text
    chunks = hide_code(text)
    new_chunks = []

    for chunk in chunks:
        errors = re.findall(r'\w{1}\s{1,2}[.,;:)]\s{1,2}\w{1}', chunk)
        for e in errors:
            temp_e = ''
            flag = False
            for c in ' '.join(e.split()):
                if (c in ['.',',',';',':',')']): flag = True
                if (flag == True): temp_e += c
                if (flag == False and c != ' '): temp_e += c

            new_chunks.append(chunk.replace(e, temp_e))

    for c, n in zip(chunks, new_chunks): new_text = new_text.replace(c, n)
    if (new_text != text): summary += '[sửa dấu câu]'

    return title, new_text, summary
    
def page_handling(page):

    title = str(page._link)
    title = title.strip('[[').strip(']]')
    summary = ''

    # hàm sửa lỗi chung, thay thế 1 số cụm từ
    if (check_redirect(page.text) == True): return title, page.text, summary
    
    title, new_text, summary = general_fixes(title, page.text, summary)
    #title, new_text, summary = punctuation_fixes(title, new_text, summary)

    return title, new_text, summary
    

def general_fixes(title, text, summary):
    """
        sửa lỗi chung
            title: tên trang - string
            text: nội dung - string
            summary: tóm tắt nội dung sửa đổi - string
            return: trả về các biến trên
    """

    new_text = text
    
    # chú thích
    new_text = re.sub(r'\{\{[Cc]ite\s*book', '{{chú thích sách', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*web', '{{chú thích web', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*news', '{{chú thích báo', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*web', '{{chú thích web', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*journal', '{{chú thích tạp chí', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*iucn', '{{chú thích IUCN', new_text)
    new_text = re.sub(r'\{\{[Cc]ite\s*doi', '{{chú thích DOI', new_text)
    new_text = re.sub(r'\{\{[Cc]ite tweet', '{{chú thích tweet', new_text)

    # tham khảo
    new_text = re.sub(r'\{\{[Rr]eflist', '{{tham khảo', new_text)
    new_text = re.sub(r'\{\{\s*[Tt]ham(\s*\_*)[Kk]hảo\s*', '{{tham khảo', new_text)
    new_text = re.sub(r'\<[Rr]eferences\s*\/\>', '{{tham khảo}}', new_text)

    # thể loại
    new_text = re.sub(r'\[\[\s*[Cc]ategory\s*:', '[[Thể loại:', new_text)
    new_text = re.sub(r'\[\[\s*[Tt]hể(\s*\_*)loại\s*:', '[[Thể loại:', new_text)

    new_text = re.sub(r'\[\[\s*[Tt]hể\s*loại\s*:\s*[Cc]ategory\s*:', '[[Thể loại:', new_text)
    new_text = re.sub(r'\[\[\s*[Tt]hể\s*loại\s*:\s*[Tt]hể\s*loại\s*:', '[[Thể loại:', new_text)

    # tập tin    
    new_text = re.sub(r'\[\[[Ff]ile\s*:', '[[Tập tin:', new_text)
    new_text = re.sub(r'\[\[[Ii]mage\s*:', '[[Hình:', new_text)

    # bản mẫu
    new_text = re.sub(r'\{\{[Tt]axobox', '{{Bảng phân loại', new_text)
    new_text = re.sub(r'\{\{[Cc]ommonscat-inline', '{{Thể loại Commons nội dòng', new_text)
    new_text = re.sub(r'\{\{[Cc]ommons category-inline', '{{Thể loại Commons nội dòng', new_text)
    new_text = re.sub(r'\{\{[Ww]ikispecies-inline', '{{Wikispecies nội dòng', new_text)
    new_text = re.sub(r'\{\{[Cc]ommons category', '{{Thể loại Commons', new_text)
    new_text = re.sub(r'\{\{[Cc]ommons\s*cat', '{{Thể loại Commons', new_text)

    # đề mục
    new_text = re.sub(r'==\s*References\s*==', '== Tham khảo ==', new_text)
    new_text = re.sub(r'==\s*External\s*links\s*==', '== Liên kết ngoài ==', new_text)
    new_text = re.sub(r'==\s*[Ll]iên\s*[Kk]ết\s*[Bb]ên\s*[Nn]goài\s*==', '== Liên kết ngoài ==', new_text)
    new_text = re.sub(r'==\s*[Ss]ee\s*[Aa]lso\s*==', '== Xem thêm ==', new_text)
    new_text = re.sub(r'==\s*[Nn]otes\s*==', '== Ghi chú ==', new_text)

    if (new_text != text): summary += '[sửa đổi chung]'

    return title, new_text, summary


def check_status(site, bot_name):
    """
        kiểm tra trạng thái bot là tắt hay mở
            site: biến đối tượng trang - object
            bot_name: tên bot - string
            return: boolean
    """

    # Kiểm tra trạng thái bot ở không gian [[Thành viên:Tên bot/Status]]
    # Xem ví dụ cách lưu ở [[Thành viên:AlphamaBot/Status]]

    page_name = 'Thành viên:' + bot_name + '/Status'
    page = pywikibot.Page(site, page_name)

    texts = page.text.split('\n')

    try:
        pair = [p.strip() for p in texts[1].split('=')]
        if (pair[0] == 'active' and pair[1] == '1'):
            return True
    except: pass

    return False


def welcome(site, welcome_template, total = 50):
    """
        chào mừng thành viên
            site: đối tượng dự án - object (site = pywikibot.Site('vi', 'wikipedia'))
            total: số lượng thành viên mới - int
            return: chào mừng thành viên có trên 1 sửa đổi     
    """

    # lấy danh sách nhật trình các tài khoản đã đăng ký mới
    log_newusers = site.logevents('newusers', total = total)

    # dựa theo nhật trình lấy danh sách tên thành viên mới
    users = (pywikibot.User(site, u.user()) for u in log_newusers)

    # kiểm tra bản mẫu có hợp lệ
    templates = ['{{thế:hoan nghênh2}}', '{{thế:hoan nghênh3}}', '{{thế:hoan nghênh4}}', '{{thế:hoan nghênh5}}',
                             '{{thế:hoan nghênh6}}', '{{thế:hoan nghênh7}}', '{{thế:hoan nghênh8}}',
                             '{{thế:hoan nghênh12}}', '{{thế:hoan nghênh của Băng Tỏa}}',
                             '{{thế:chào mừng thành viên mới}}']
    
    welcome_template = welcome_template.lower()
    if (welcome_template not in templates):
        print('Bản mẫu chào mừng không hợp lệ! Kiểm tra danh sách: ', templates)
        return

    # bắt đầu duyệt danh sách thành viên mới
    for u in users:
        try:
            # lấy tên thành viên
            username = str(u._link)
            username = username.strip('[[').strip(']]')
            username = username.replace('Thành viên:', '')
     
            # kiểm tra hợp lệ
            if u.isBlocked():  continue # không chào mừng nếu thành viên bị cấm
            if 'bot' in u.groups() or 'bot' in username.lower(): continue  # không chào mừng nếu thành viên là bot
            if u.editCount() < 1: continue # không chào mừng nếu thành viên không có sửa đổi nào

            # không chào mừng nếu thành viên có tên vi phạm,...
              
            print('Đang chào mừng thành viên: ', username)
            user_talk = 'Thảo luận Thành viên:' + username
            page = pywikibot.Page(site, user_talk)

            # xử lý trang
            if (len(page.text) == 0):
                page.text += welcome_template + '\n~~~~'
                page.save(summary = '[[Thành viên:AnsterBot|Task 0]] - [[:mw:Manual:Pywikibot/vi|Pywikibot]]: Chào mừng thành viên mới (bản mẫu ' + welcome_template + ').')
                print('--- Đã thêm bản mẫu.')
            else: print('--- Trang thảo luận đã tồn tại.')
        except:
            print('--- Tên thành viên chứa ký tự nằm ngoài BMP.')
            pass
            
        print('....................................')
            

def multifunction(site):
    """
        hàm đa năng
            site: đối tượng dự án (object)
    """
    
    # các hàm tạo danh sách
    # total: tổng số trang cần tìm
    # namespaces: không gian tên
    # pages = site.search('toán học', total=50, namespaces=[0]) # tìm trang theo cụm từ
    # pages = site.search('insource: 'toán học'', total=50, namespaces=[0]) # tìm trang bằng mã wiki
    # pages = RecentChangesPageGenerator(site, total = 50, namespaces=[0]) # tìm trang thay đổi gần đây
    # pages = RandomPageGenerator(site, total = 50, namespaces=[0]) # lỗi thời
    # pages = NewpagesPageGenerator(site, total=1000, namespaces=[0]) # tìm danh sách các trang gần đây ở không gian Chính (bài viết)

    #pages = site.randompages(total=500, namespaces=[0], redirects=True) # lấy danh sách bài ngẫu nhiên

    pages = site.randompages(total=500, namespaces=[0], redirects=True) # lấy danh sách bài ngẫu nhiên
    
    step = 5
    count = 1

    for p in pages:
        count += 1

        try:
            print('....................................')

            # mỗi 5 trang thì mới kiểm tra trạng thái bot tắt hay mở
            if (count%step == 0):
                if (check_status(site, bot_name) == False):
                    print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
                    break
                    
                start = time.time()
                temp_title = str(p._link)
                temp_title = temp_title.strip('[[').strip(']]')
                print('Đang xử lý trang: ', temp_title)
                    
                page = pywikibot.Page(site, temp_title)

                # xử lý trang
                title, new_text, summary = page_handling(page)
    
                if (new_text !=  page.text):
                    page.text = new_text
                    end = time.time()

                    time_label = str(end - start)[0:6] + 's'
                    page.save(summary = '[[Thành viên:AnsterBot|Task 0]] - [[:mw:Manual:Pywikibot/vi|Pywikibot]] + [[Thành viên:AlphamaBot/Code đa chức năng (pywikibot)|AlphamaModule]]: ' + summary + ', ' + time_label) # lưu trang
                                                              
                    print('--- Đã lưu!')
                else:
                    print('--- Không có gì thay đổi!')
                    
        except Exception as e:
            print('Lỗi: ', e, p)

        


def menu(argv, site):
    """
        lấy tham số truyền theo dòng lệnh
            argv: đối số - object
            site: dự án - object
    """

    try:
        opts, args = getopt.getopt(argv, "h:f:")
    except getopt.GetoptError:
        print('AlphamaModule.py -f <welcome|multi|all>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('AlphamaModule.py -f <welcome|multi|all>')
            sys.exit()
        elif(opt in ('-f')):
            if (arg == 'multi'):
                multifunction(site)
            elif (arg == 'welcome'):
                welcome(site, '{{thế:hoan nghênh12}}', total = 500)
            elif (arg == 'all'):
                multifunction(site)
                welcome(site, '{{thế:hoan nghênh12}}', total = 500)
            else:
                print('AlphamaModule.py -f <welcome|multi|all>')

#.......................................................................................
if __name__ == '__main__':


    site = pywikibot.Site('vi', 'wikipedia') # khai báo ngôn ngữ + dự án

    # ghi đè tham số trong config.py
    bot_name = 'AnsterBot'
    usernames['wikipedia']['vi'] = bot_name # tên bot
    console_encoding = 'utf-8'
    use_api_login = True 

    put_throttle = 0 # bỏ thời gian chờ giữa các action
    maxthrottle = 0 # bỏ thời gian chờ tối đa giữa các action
    noisysleep = 30

    # Tạo thao tác lưu ảo để đăng nhập và kiểm tra chức năng bot
    bot_status_page = 'Thành viên:' + bot_name + '/Status'
    page = pywikibot.Page(site, bot_status_page)
    page.save('')

    if (check_status(site, bot_name) == False):
        print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
        sys.exit() # hàm thoát trong main


    # sử dụng menu console
    menu(sys.argv[1:], site)

    # hàm chào mừng
    #welcome(site, '{{thế:hoan nghênh12}}', total = 500)

    # hàm chào mừng chạy liên tục
    '''i = 0
    while True:
        if (i%5 == 0):
            if (check_status(site, bot_name) == False):
                print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
                break
        i = i + 1
        welcome(site, '{{thế:hoan nghênh12}}', total = 500)'''

    # hàm đa năng xử lý trang
    #multifunction(site)

    # hàm đa năng xử lý trang chạy liên tục
    '''i = 0
    while True:
        if (i%5 == 0):
            if (check_status(site, bot_name) == False):
                print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
                break
        i = i + 1
        multifunction(site)'''

    # hàm tổng hợp
    #welcome(site, '{{thế:hoan nghênh12}}', total = 500)
    #multifunction(site)

    # hàm tổng hợp chạy liên tục
    i = 0
    while True:
        if (i%5 == 0):
            if (check_status(site, bot_name) == False):
                print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
                break
        i = i + 1
        # welcome(site, '{{thế:hoan nghênh12}}', total = 500)
        multifunction(site)