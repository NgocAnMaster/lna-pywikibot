"""
    TASK CỦA ANSTERBOT
    Từ NgocAnMaster
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

def TechNews(site, temp_page, dest_pages):
    """
        TRANG TECH NEWS (Bản tin Kỹ thuật hàng tuần)
        Tham số:
            site: đối tượng dự án - object (site = pywikibot.Site('vi', 'wikipedia'))
            temp_page: trang tạm thời dùng để lưu bản tin kỹ thuật. Bot sẽ tẩy trống định kỳ.
                Để tránh việc phá hoại, nội dung của trang phải trên 500 byte. Lúc đó, nội dung của trang sẽ được bot đưa vào các trang mục tiêu.
            dest_pages: các trang đích để bot gửi nội dung.
    """
    # kiểm tra dest_page
    if len(dest_pages) == 0:
        print('Lỗi: Danh sách trang đích trống! Vui lòng kiểm tra lại.')
        return
    try:
        # Lấy nội dung trang tmp
        tmp_page_content = pywikibot.Page(site, temp_page)
        print('Đang chép nội dung trang nguồn ' + temp_page + '...')
        # Không thực hiện nếu trang temp nhỏ hơn 500 bytes
        if len(tmp_page_content.text) < 500:
            print('Trang nguồn có kích cỡ nhỏ hơn 500 bytes. Bot sẽ tẩy trống trang này.')
        else:
            # Ghi nội dung có trên trang
            content = tmp_page_content.text
            print('Đang dán nội dung vào trang đích...')
            # Dán vào từng trang đích một
            for dest_page in dest_pages:
                print('- ' + dest_page + '...', end = ' ')
                dest_content = pywikibot.Page(site, dest_page)
                dest_content.text += '\n\n' + content
                dest_content.save(summary = '(Bot) Thông tin về Bản tin Kỹ thuật tuần mới nhất', minor=False)
                print('xong.')
        # Bảo trì
        print('Đang dọn dẹp nội dung của trang tạm Bản tin kỹ thuật...')
        tmp_page_content.text = ''
        tmp_page_content.save(summary = '(Bot) Bảo trì trang tạm cho Bản tin Kỹ thuật')
        print('Hoàn thành.')
    except pywikibot.exceptions.IsRedirectPageError:
        print('Lỗi: Đã phát hiện trang đổi hướng. Vui lòng kiểm tra lại.')
        return
    
def clean_sandbox(site, sandboxes):
    """
        HÀM DỌN DẸP CHỖ THỬ
        clean_sandbox(sandboxes)
        Trong đó, sandboxes là một list các array dạng
        [[page1, content1], [page2, content2], ..., [pagen, contentn]]
        với pagei (i = 1, 2, ... n) là tên trang chỗ thử cần dọn dẹp
        và contenti là nội dung cần dọn dẹp trong chỗ thử.
        Trang chỉ được dọn dẹp khi 
    """
    if len(sandboxes) == 0: # list trống
        pywikibot.error('Không có trang nào được chỉ định - vui lòng kiểm tra lại!')
        return
    print('----------------------------------------------------\nĐang tiến hành dọn dẹp chỗ thử của các trang đã chọn...')
    for sandbox in sandboxes:
        try:
            print('- ' + sandbox[0] + '...')
            sbpage = pywikibot.Page(site, sandbox[0]) # mở trang chỗ thử chỉ định trong pagei
            template = sandbox[1] # ghi nội dung của contenti, dùng \n để xuống dòng
            lts = sbpage.latest_revision.timestamp.posix_timestamp()
            current_time = time.time()
            print('Sửa đổi cuối cùng được thực hiện', current_time - lts, 'giây trước')
            if sbpage.text != template and current_time - lts > 900:
                sbpage.text = template
                sbpage.save(summary = '(Bot) Dọn dẹp trang chỗ thử')
                print('Đã dọn dẹp!')
            else:
                print('Không có thay đổi gì - đã bỏ qua.')
        except:
            pywikibot.error('Có lỗi xảy ra khi xử lý trang ' + sandbox[1])
            traceback.print_exc()
            # continue
        finally:
            print('----------------------------------------------------')
    print('Dọn dẹp chỗ thử hoàn tất.')

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

def maintainanceCategoryCreator(site, page, content, summary):
    """
        HÀM TẠO THỂ LOẠI BẢO TRÌ THEO YÊU CẦU
        Tự động tạo thể loại bảo trì với nội dung theo yêu cầu.
        Cú pháp: maintainanceCategoryCreator(site, page, content, summary)
        Trong đó:
            site là mã wiki được hỗ trợ bởi Pywikibot.
            page là tên trang cần tạo thể loại. Trang này PHẢI LÀ MỘT THỂ LOẠI.
            content là nội dung cần đưa vào thể loại bảo trì.
            summary là nội dung tóm lược sửa đổi tùy chỉnh để bot thực hiện lưu sửa đổi.
        Task tự động tạo thể loại sẽ hữu ích đối với các thể loại bảo trì mà cần được xếp
        theo ngày, chẳng hạn như [[Thể loại:Hình có vấn đề]] và [[Thể loại:Bài chất lượng
        kém]]. Lưu ý rằng bot chỉ tạo thể loại nếu trang đó chưa tồn tại và đã có trang
        trong thể loại đó, nhằm hạn chế việc tạo thể loại trống.
    """
    try:
        cat = pywikibot.Category(site, page)
        print('Đang mở ' + str(cat.title(with_section=False)) + '...')
        # tp = pywikibot.Page(site, page)
        if cat.exists():
            print('Thể loại này đã tồn tại - đã bỏ qua việc tạo thể loại được yêu cầu.')
            return
    except ValueError:
        pywikibot.error('Trang mà bạn chỉ định không thuộc không gian tên Thể loại. Vui lòng kiểm tra lại.')
        return
    if cat.isEmptyCategory():
        print('Không có trang hoặc thể loại liên kết nào trong đây - đã bỏ qua việc tạo thể loại được yêu cầu.')
        return
    print('Thể loại hiện có trang liên kết nhưng chưa được tạo. Đang tạo...')
    try:
        cat.text = content
        cat.save(summary)
    except:
        pywikibot.error('Có lỗi xảy ra khi xử lý trang ' + cat.title())
        traceback.print_exc()
        return

def maintainanceCatComboTask(site, pages):
    """
        Hàm gói để thực hiện các task tạo thể loại bảo trì được yêu cầu.
        Cú pháp: maintainanceCatComboTask(site, pages)
        Trong đó:
            site là mã wiki được hỗ trợ bởi Pywikibot.
            pages là một list() trang thể loại - là bộ ba [page, content, summary]
            với page là tên THỂ LOẠI, content là nội dung sẽ được thêm vào
            nếu thể loại chưa tồn tại và summary là tóm lược sửa đổi.
    """
    print('Đang kiểm tra và tạo các thể loại bảo trì được yêu cầu...')
    for page in pages:
        maintainanceCategoryCreator(site, page[0], page[1], page[2])
        print('----------------------------------------------------')
    print('Kiểm tra hoàn tất.')

# để hạn chế việc khi ứng dụng đang chạy, "hôm nay là ngày 2 nhưng lại kiểm tra thể loại ngày 1"
def DatedMaintainance():
    """
        HÀM DatedMaintainance
        Tự điều chỉnh hàm này để xét các trang được yêu cầu
    """
    today = datetime.now(timezone.utc)
    str1 = today.strftime('%Y-%m-%d')
    str2 = today.strftime('%d-%m-%Y')
    ystr = str1[:4:]
    mstr = str1[5:7:]
    dstr = str1[8::]
    sum = '(Bot) Tạo thể loại bảo trì theo ngày'
    pages = [['Thể loại:Bài chất lượng kém ' + str2, '{{subst:Bài chất lượng kém đầu}}', sum], ['Thể loại:Hình có vấn đề ' + str1, '{{subst:Hình có vấn đề đầu}}', sum], ['Thể loại:Hình không rõ nguồn gốc ' + str1, '{{subst:Hình không rõ nguồn gốc đầu |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum], ['Thể loại:Hình không rõ tình trạng bản quyền ' + str1, '{{subst:Hình không rõ tình trạng bản quyền đầu |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum], ['Thể loại:Hình thiếu mô tả hợp lý ' + str1, '{{subst:Hình thiếu mô tả hợp lý |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum], ['Thể loại:Hình không tự do có thể thay thế ' + str1, '{{subst:Đầu thể loại con hình không tự do có thể thay thế |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum], ['Thể loại:Hình sử dụng hợp lý không sử dụng ' + str1, '{{subst:Đầu thể loại con hình sử dụng hợp lý không sử dụng |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum], ['Thể loại:Đề nghị xóa ' + str1, '{{subst:Đầu thể loại con đề nghị xóa |4=' + ystr + ' |2=' + mstr + ' |1=' + dstr + '}}', sum]]
    maintainanceCatComboTask(site, pages)

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

# Mỗi ngày lúc 18:00, kiểm tra trang nguồn
schedule.every().day.at("18:00").do(TechNews, site, 'Thảo luận Thành viên:AnsterBot/Bản tin kỹ thuật', ['Wikipedia:Bản tin kỹ thuật'])

# Cứ mỗi 20 phút, dọn dẹp chỗ thử
sandboxes = [['Trợ giúp:Chỗ thử', ''], ['Thành viên:Hộp cát', '{{mbox\n| type=notice\n| image=<!--none-->\n| textstyle=text-align:center;\n| text=Đây là một tài khoản thay thế của {{noping|NguoiDungKhongDinhDanh}}, được mở nhằm mục đích thử nghiệm công cụ.<br>[[/Bộ lọc sai phạm/|Danh sách bộ lọc sai phạm]]\n}}[[Thể loại:Tài khoản người dùng ví dụ và thử nghiệm]]\n{{Đầu chỗ thử}}<!--\n*                    Chào mừng đến với trang chỗ thử!                    *\n*                      Vui lòng để nguyên phần này                       *\n*                   Trang này sẽ được dọn dẹp định kỳ                    *\n*           Hãy tự do thể hiện kỹ năng sửa đổi của bạn bên dưới          *\n■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■-->\n'], ['Thảo luận Thành viên:Hộp cát', '{{Đầu chỗ thử}}<!--\n*                    Chào mừng đến với trang chỗ thử!                    *\n*                      Vui lòng để nguyên phần này                       *\n*                   Trang này sẽ được dọn dẹp định kỳ                    *\n*           Hãy tự do thể hiện kỹ năng sửa đổi của bạn bên dưới          *\n■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■-->\n']]
schedule.every(10).minutes.do(clean_sandbox, site, sandboxes)

# hàng ngày, lúc 18:00 thực hiện hàm này
data_page = 'Wikipedia:Báo cáo cơ sở dữ liệu/Danh sách trang bị khóa nhiều lần nhất'
schedule.every().day.at("18:00").do(most_protected_pages, site, data_page)

# mỗi giờ kiểm tra thể loại bảo trì được yêu cầu trong hàm DatedMaintainance
schedule.every().hour.do(DatedMaintainance)

# cuối cùng, thực hiện chức năng
TechNews(site, 'Thảo luận Thành viên:AnsterBot/Bản tin kỹ thuật', ['Wikipedia:Bản tin kỹ thuật'])
DatedMaintainance()
# most_protected_pages(site, 'Wikipedia:Báo cáo cơ sở dữ liệu/Danh sách trang bị khóa nhiều lần nhất')

# Schedule, trong lúc đó phải kiểm tra file nguồn
while True:
    if (check_status(site, bot_name) == False):
        print('Bot không được kích hoạt! Xem ở [[' + bot_status_page + ']].')
        sys.exit() # hàm thoát trong main
    schedule.run_pending()
    time.sleep(1)
# tmp_page_content = pywikibot.Page(site, 'Thành viên:AnsterBot/Bản tin kỹ thuật')
# print(tmp_page_content.text)