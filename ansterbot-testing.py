"""
    CHỖ THỬ CỦA ANSTERBOT
    Từ NgocAnMaster

    *** LƯU Ý QUAN TRỌNG - CHỈ DÙNG CHO THỬ NGHIỆM ***
    Nội dung này bao gồm các đoạn mã thử nghiệm có thể gây lỗi
    trong quá trình thí nghiệm tính năng mới.
    KHÔNG sử dụng đoạn mã này để vận hành chính thức!
    Nếu bạn đã hoàn thành việc thử nghiệm và cần vận hành chính thức,
    hãy di chuyển các hàm đó sang script Python chính thức.
    
    *** GIẤY PHÉP ***
    Bot hoạt động với giấy phép MIT. Theo giấy phép này,
    bạn được tự do tái phân phối lại cho bất kỳ người
    nào có bản sao của phần mềm bot này
    cũng như các tài liệu có liên quan ("Phần mềm")
    để sử dụng mà không bị hạn chế, bao gồm nhưng không
    giới hạn các quyền sử dụng, sao chép, sửa đổi,
    hợp nhất, xuất bản, phân phối, cấp phép lại và/hoặc
    bán các bản sao của Phần mềm và cho phép những người
    được cung cấp Phần mềm làm như vậy, tuân theo các
    điều khoản và điều kiện nhất định.
"""
import sys, getopt
import pywikibot

from pywikibot.pagegenerators import * # pagegenerators: tìm kiếm danh sách trang
from pywikibot.config import * # config: cấu hình bot (user, password,...)
#from pywikibot.login import *

import re # gói regex dành cho các biểu thức chính quy
import time
import schedule
import traceback

# dùng để thực hiện json
import json
import requests

# dùng cho các tác vụ thời gian
import datetime
from datetime import datetime, timezone


# -- helpers -------------------------------------------------- #
# ------------------------------------------------------------- #
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

def checkOrphanTag():
    """
        HÀM KIỂM TRA BÀI MỒ CÔI
        Nhằm hạn chế việc gây tranh cãi liên quan đến việc biển mồ côi gắn quá sớm,
        mỗi ngày hàm này sẽ giúp bot loại bỏ bản mẫu mồ côi trên các trang được tạo chưa đầy 1 năm.
        Cú pháp: checkOrphanTag(). Hàm này không cần nhận tham số nào.
        Bot kiểm tra các bài viết trong [[Thể loại:Bài mồ côi]] (CHỈ BÀI VIẾT mới được kiểm tra).
        Sau đó, bot kiểm tra phiên bản cũ nhất của bài viết và đối chiếu với thời điểm hiện tại.
        Nếu bài viết bắt đầu được viết cách đây hơn 1 năm, bot sẽ tự động bỏ qua bài viết đó.
        Nếu không, bot tìm kiếm bản mẫu {{mồ côi}} (hoặc alias của nó) và gỡ ra khỏi bài viết.
    """
    orphan_tags = ['{{mồ côi', '{{bài mồ côi', '{{orphan', '{{unlinked']
    print('Đang phân tích [[Thể loại:Bài mồ côi]]...')
    orphan_cat = pywikibot.Category(site, 'Thể loại:Bài mồ côi')
    orphan_articles = list(orphan_cat.articles(recurse=0, namespaces=0))
    if len(orphan_articles) == 0:
        print('Không có bài viết mồ côi nào trong thể loại này - kiểm tra hoàn tất.')
        return
    print('Đã tìm thấy ' + str(len(orphan_articles)) + ' bài viết trong thể loại.')
    print('Đang kiểm tra các bài viết trong thể loại...')
    count = 0
    fixed = 0
    for p in orphan_articles:
        count += 1
        print('----------------------------------------------------\n' + str(count) + '. ' + p.title())
        try:
            first_rev = p.oldest_revision.timestamp.posix_timestamp()
            current_time = time.time()
            if current_time - first_rev >= 31536000:
                print('Bài viết này được tạo ra cách đây hơn 1 năm - đã bỏ qua bài viết này.')
            else:
                print('Bài viết này được tạo ra dưới 1 năm.')
                fixed += 1
        except Exception as e:
            pywikibot.error('Có lỗi xảy ra khi xử lý trang ' + p.title())
            traceback.print_exc()
            pywikibot.info('Đã bỏ qua bài viết do có lỗi.')
            continue
    print('Kiểm tra hoàn tất. Bot đã sửa ' + str(fixed) + 'bài viết.')

def get_namespace(ns, prefixed: bool = False):
    """
        HÀM LẤY KHÔNG GIAN TÊN DỰA TRÊN MÃ KHÔNG GIAN TÊN
        Cú pháp: get_namespace(ns, prefixed)
        Trong đó ns là mã không gian tên hợp lệ.
        Xem thêm tại [[Wikipedia:Không gian tên]].
        Mặc định nếu không có mã không gian tên hoặc mã bằng 0 sẽ trỏ về
        không gian tên Bài viết.
        prefixed chỉ định rằng đây có phải prefix (tiền tố) hay không.
    """
    nss = ''
    if ns == 1:
        nss = 'Thảo luận'
    elif ns == 2:
        nss = 'Thành viên'
    elif ns == 3:
        nss = 'Thảo luận Thành viên'
    elif ns == 4:
        nss = 'Wikipedia'
    elif ns == 5:
        nss = 'Thảo luận Wikipedia'
    elif ns == 6:
        nss = 'Tập tin'
    elif ns == 7:
        nss = 'Thảo luận Tập tin'
    elif ns == 8:
        nss = 'MediaWiki'
    elif ns == 9:
        nss = 'Thảo luận MediaWiki'
    elif ns == 10:
        nss = 'Bản mẫu'
    elif ns == 11:
        nss = 'Thảo luận Bản mẫu'
    elif ns == 12:
        nss = 'Trợ giúp'
    elif ns == 13:
        nss = 'Thảo luận Trợ giúp'
    elif ns == 14:
        nss = 'Thể loại'
    elif ns == 15:
        nss = 'Thảo luận Thể loại'
    elif ns == 100:
        nss = 'Cổng thông tin'
    elif ns == 9:
        nss = 'Thảo luận Cổng thông tin'
    elif ns == 828:
        nss = 'Mô đun'
    elif ns == 829:
        nss = 'Thảo luận Mô đun'
    if nss != '' and prefixed:
        nss += ':'
    return nss

def most_protected_pages(site, dest):
    """
        HÀM LẤY DỮ LIỆU CÁC TRANG ĐƯỢC KHÓA NHIỀU NHẤT
        Cú pháp: most_protected_pages(site, dest)
        Trong đó, site là tên trang wiki;
        dest là tên trang cần dán nội dung.
        Dữ liệu được lấy từ trang https://quarry.wmcloud.org/query/60657.
    """
    try:
        print('Đang lấy nội dung trang dữ liệu...')
        # Lấy nội dung từ Quarry
        url = 'https://quarry.wmcloud.org/query/60657/result/latest/0/json'
        response = requests.get(url)
        data = json.loads(response.text)

        # Mở trang đích được chỉ định trong hàm
        print('Đang mở trang đích "' + dest + '"...')
        stats_page = pywikibot.Page(site, dest)

        # Lưu dữ liệu vào trong trang đích
        print('Đang lưu dữ liệu...')
        content = '{{/Đầu}}\n' # template đầu trang
        rows_data = data['rows'] # dữ liệu bằng dữ liệu trong rows
        for i in range(1000): # tra trong 1000 dữ liệu đầu tiên
            row = rows_data[i]
            ns = get_namespace(row[0], True) # hàm gọi không gian tên
            protected_page = row[1].replace('_', ' ') # thay thế "_" bằng dấu cách
            occurrences = row[2]
            lp = str(row[3]) # timestamp, đổi sang string để nối
            last_protected = lp[0:4:] + '-' + lp[4:6:] + '-' + lp[6:8:] + ' ' + lp[8:10:] + ':' + lp[10:12:] + ':' + lp[12:14:] # convert thành dạng str. timestamp phải đúng định dạng YYYYMMDDHHMMSS
            content += '|-\n!' + str(i+1) + '\n|[[:' + ns + protected_page + ']]\n|' + str(occurrences) + '\n|' + last_protected + '\n' # nối tất cả lại thành một dòng của bảng và đưa vào content
        content += '|}\nLần cập nhật cuối: ~~~~~' # kết bảng
        stats_page.text = content
        stats_page.save(summary = '(Bot) Cập nhật dữ liệu các trang được khóa nhiều nhất') # lưu lại
        print('Xong!')
    except:
        pywikibot.error('Có lỗi xảy ra khi xử lý trang ' + dest)
        traceback.print_exc()

"""
    HÀM CHÍNH
    Lưu ý điền đúng tên trang được chỉ định trong các hàm được yêu cầu.
    Tên trang PHẢI LÀ tên đã tồn tại trên vi.wikipedia và KHÔNG PHẢI trang đổi hướng.
"""
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

# cat = pywikibot.Category(site, 'Thể loại:Chờ xóa')
# res = list(cat.articles(recurse=1, namespaces=0))
# for p in res:
#     print(p.title(), type(p.title()))
#     print(p.text)
# checkOrphanTag()
# orphans = ['{{mồ côi', '{{bài mồ côi', '{{orphan', '{{unlinked']
# test_page = pywikibot.Page(site, '2024')
# print(list(test_page.backlinks(namespaces=0)))

data_page = 'Wikipedia:Báo cáo cơ sở dữ liệu/Danh sách trang bị khóa nhiều lần nhất'
most_protected_pages(site, data_page)