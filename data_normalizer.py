import re
import data_utilities
from fuzzywuzzy import process
import constants


def normalize(text, norm_type="none"):
    text = data_utilities.compound2unicode(text)
    text = re.sub('Mười', '10', text)
    text = re.sub('mười', '10', text)
    text = data_utilities.remove_vietnamese_accent(text)

    if norm_type == constants.LABEL_PRICE:
        low, high = normalize_price(text)
        return low, high

    elif norm_type == constants.LABEL_AREA:
        low, high = normalize_area(text)
        return low, high

    elif norm_type == constants.LABEL_FLOOR:
        floor_name, floor_num = normalize_floor(text)
        return {"type": floor_name, "value": floor_num}

    elif norm_type in [
            constants.LABEL_BED_ROOM, constants.LABEL_BATH_ROOM,
            constants.LABEL_LIVING_ROOM
    ]:
        room_name, room_num = normalize_room(text)
        return room_num

    elif norm_type == constants.LABEL_CITY:
        text = normalize_city(text)

    elif norm_type == constants.LABEL_DISTRICT:
        text = normalize_district(text)

    elif norm_type == constants.LABEL_WARD:
        text = normalize_ward(text)

    elif norm_type == constants.LABEL_STREET:
        text = normalize_street(text)

    elif norm_type == constants.LABEL_LEGAL:
        text = normalize_legal(text)

    elif norm_type == constants.LABEL_DIRECTION:
        text = normalize_direction(text)

    elif norm_type == constants.LABEL_POSITION:
        text = normalize_position(text)

    elif norm_type == constants.LABEL_USAGE:
        text = normalize_usage(text)

    elif norm_type == constants.LABEL_REAL_ESTATE_TYPE:
        text = normalize_real_estate_type(text)

    elif norm_type == constants.LABEL_TRANSACTION:
        text = normalize_transaction(text)

    elif norm_type in [
            constants.LABEL_ROAD_WIDTH, constants.LABEL_FRONT_LENGTH
    ]:
        text = normalize_numeric(text)

    return text


main_divider = '-'
dividers = ['toi', 'va', '~', 'hoac']
currency_unit = ['ti', 'ty', 'trieu', 'tr', 'nghin', 'ngan', 'k']
maping_num = {
    'mot': '1',
    'hai': '2',
    'ba': '3',
    'bon': '4',
    'nam': '5',
    'sau': '6',
    'bay': '7',
    'tam': '8',
    'chin': '9'
}


# ---------- Normalize price ----------
def normalize_price(text):
    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    # Replace text.
    text = text.replace('ti', 'ty')
    text = text.replace('tram', '##00')
    text = text.replace('trieu', 'tr')
    text = text.replace('muoi', '##0')  ## Mươi.
    text = text.replace(' ##', '')
    text = text.replace('ruoi', '5')  ## Rưỡi.
    text = text.replace('mot', '1')  ## Mốt.
    text = text.replace('k', 'kk')
    text = text.replace('nghin', 'kk')
    text = text.replace('ngan', 'kk')
    text = text.replace('dong', 'vnd')
    text = text.replace(',', '.')
    text = text.replace('<', '')

    # Replace with the main divider '-' between the 2 prices.
    for div in dividers:
        text = re.sub(div, main_divider, text)

    price_list = list()
    arr = text.split(main_divider)
    ##     print('Divided: ', arr)

    biggest_unit = None
    for element in reversed(arr):
        prices = powerful_split_price(element)
        ##         print('Splited: ', prices)
        for price in reversed(prices):
            value, unit = normalize_price_unit(price, biggest_unit)
            if value == 0:
                continue
            price_list.append(value)
            biggest_unit = unit


##             print(biggest_unit)
    if len(price_list) == 0:
        low, high = None, None
    elif len(price_list) == 1:
        low, high = price_list[0], None
    else:
        low, high = min(price_list), max(price_list)
    return low, high

re_num = '\d+(\s*\.\s*\d+)?'
re_vnd = re.compile('(\d+(\s*\.\s*\d+)?\svnd)')
re_hud = re.compile('(\d+(\s*\.\s*\d+)?\skk)')
re_mil = re.compile('(\d+(\s*\.\s*\d+)?\str)')
re_bil = re.compile('(\d+(\s*\.\s*\d+)?\sty)')


def powerful_split_price(text):
    text = text.strip()
    idx_bil = [0] + [i.start()
                     for i in re.finditer(re_bil, text)] + [len(text)]
    idx_mil = [0] + [i.start()
                     for i in re.finditer(re_mil, text)] + [len(text)]
    idx_hud = [0] + [i.start()
                     for i in re.finditer(re_hud, text)] + [len(text)]
    idx_vnd = [0] + [i.start()
                     for i in re.finditer(re_vnd, text)] + [len(text)]
    ##     print('idx_bil', idx_bil)
    ##     print('idx_mil', idx_mil)
    ##     print('idx_hud', idx_hud)
    price_list = list()
    if len(idx_bil) > 2:
        for i in range(0, len(idx_bil) - 1):
            price = text[idx_bil[i]:idx_bil[i + 1]]
            if price != '':
                price_list.append(price)
    elif len(idx_mil) > 2:
        for i in range(0, len(idx_mil) - 1):
            price = text[idx_mil[i]:idx_mil[i + 1]]
            if price != '':
                price_list.append(price)
    elif len(idx_hud) > 2:
        for i in range(0, len(idx_hud) - 1):
            price = text[idx_hud[i]:idx_hud[i + 1]]
            if price != '':
                price_list.append(price)
    elif len(idx_vnd) > 2:
        for i in range(0, len(idx_vnd) - 1):
            price = text[idx_vnd[i]:idx_vnd[i + 1]]
            if price != '':
                price_list.append(price)
    elif text != '':
        price_list.append(text)
    return price_list


maping_unit = {'ty': 1000000000, 'tr': 1000000, 'kk': 1000, 'vnd': 1}


def normalize_price_unit(text, pre_unit):
    if text == '':
        return None, None

    final_value = 0

    arr = text.split(' ')

    if pre_unit is None:
        pre_unit = 'vnd'

    current_unit = pre_unit

    num_list = [
        float(re.sub(' ', '', i.group())) for i in re.finditer(re_num, text)
    ]

    unit_list = [i.group() for i in re.finditer('[a-z]+', text)]
    ##     if 'vnd' not in len(unit_list):
    ##         unit_list.append('vnd')
    ##     print('Num list: ', num_list)
    ##     print('Unit list: ', unit_list)

    if len(unit_list) == 0:

        final_value = num_list[-1] * maping_unit[pre_unit]
        return final_value, pre_unit

    odd_unit = 'vnd'
    for i in range(min(len(num_list), len(unit_list))):
        num = num_list[i]
        unit = unit_list[i]
        if unit in maping_unit.keys():
            final_value += maping_unit[unit] * num
            odd_unit = unit
    if len(num_list) > len(unit_list):
        odd = num_list[len(unit_list)]
        if odd < 10:
            final_value += maping_unit[odd_unit] * odd / 10
        else:
            final_value += maping_unit[odd_unit] * odd / 1000

##     print(final_value, odd_unit)
    return final_value, odd_unit


# ---------- Area ----------
area_divider = ['dai', 'rong', 'nhan', '\*']
re_num_with_unit = '(\d+(\s*\.\s*\d+)?)(\s*(m\^|km\^|m|km|ha))?'
re_num_n_x = '(' + re_num_with_unit + '\s*x\s*)'
re_powerful_x = re_num_n_x + '+' + re_num_with_unit


# Normalize area
def normalize_area(text):
    # Replace 'dai', 'rong', 'nhan', '\*' to 'x'.
    for div in area_divider:
        text = text.replace(div, 'x')

    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    # Replace text.
    text = text.replace(',', '.')
    text = text.replace('.', ' . ')
    text = text.replace('x', ' x ')
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    text = text.replace('kilo met', 'km')
    text = text.replace('met', 'm')
    text = text.replace('vuong', '2')
    text = text.replace('m 2', 'm^')
    text = text.replace('m2', 'm^')
    text = text.replace('hecta', 'ha')
    text = text.replace('hec ta', 'ha')
    text = text.replace('hec', 'ha')

    area_list = list()
    pre_RHS = '0'  ##right hand side

    if 'x' in text:
        x_group = [i.group() for i in re.finditer(re_powerful_x, text)]
        for x in x_group:
            text = text.replace(x, '')
            area_list += normalize_area_x(x)

    # Determine the low and high values of the area.
    non_x_group = [i.group() for i in re.finditer(re_num_with_unit, text)]

    for x in non_x_group:
        area_list.append(normalize_area_non_x(x))
    if len(area_list) == 0:
        low, high = None, None
    elif len(area_list) == 1:
        low, high = area_list[0], None
    else:
        low, high = min(area_list), max(area_list)
    return low, high


def normalize_area_x(text):
    factor = 1
    if 'km' in text:
        factor = 1000000
    text = re.sub('[^\d\.x]', '', text)
    area_list = list()
    arr = [float(i) for i in text.split('x')]
    for i in range(len(arr) - 1):
        area = arr[i] * arr[i + 1] * factor
        area_list.append(area)
    return area_list


def normalize_area_non_x(text):
    factor = 1
    if 'km' in text:
        factor = 1000000
    elif 'ha' in text:
        factor = 10000
    text = re.sub('[^\d\.]', '', text)
    return float(text) * factor


# ---------- Room ----------
re_rooms = [
    r"s(an)?\W*t(huong)?", r"san\b", r"(p(hong)?)?\W*t(ro)?|\btro\b",
    r"(p(hong)?)?\W*n(gu)?|\bngu\b", r"(p(hong)?)?\W*g(ia[tc])?|\bgia[tc]\b",
    r"(p(hong)?)?\W*t(ho)?\b|\btho\b", r"(p(hong)?)?\W*k(hach)?|\bkhach\b",
    r"n(ha)?\W*k(ho)?|\bkho\b", r"gara|o\W*to|xe\W*hoi", r"xe(\W*may)?",
    r"ki\W*o[ts]", r"(gieng\W*)?troi", r"van\W*phong|k(inh)?\W+d(oanh)?",
    r"ba[nl]g?\W*co(ng?|l)", r"(p(hong)?)?\W*(b(ep)?|\ban\b)|\bbep\W*an\b",
    r"(p(hong)?)?\W*(tam|v(e)?\W*s(inh)?|wc|toi?ll?e?t)",
    r"(p(hong)?)?\W+l(am)?\W+v(iec)?", r"(p(hong)?)?\W+s(inh)?\W+h(oat)?"
]

room_name = [
    "san thuong", "san", "phong tro", "phong ngu", "phong giat", "phong tho",
    "phong khach", "nha kho", "gara", "xe may", "kiots", "gieng troi",
    "van phong", "ban cong", "bep an", "nha ve sinh", "phong lam viec",
    "phong sinh hoat"
]


# Normalize room
def normalize_room(text):
    text = text.split()
    temp = text[-1]
    text = ' '.join(text[:-1])

    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    text = text + ' ' + temp
    num_arr = [i.group() for i in re.finditer(re_num, text)]
    num_arr = [int(float(i.replace(' ', ''))) for i in num_arr]

    if len(num_arr) > 0:
        num_room = min(num_arr)
    else:
        num_room = 1

    current_key = ''
    current_idx = -1

    for idx, regex in enumerate(re_rooms):
        ##         print(text)
        keys = [i.group() for i in re.finditer(regex, text)]
        ##         print(idx, keys)
        if len(keys) > 0 and len(current_key) < len(max(keys, key=len)):
            current_key = max(keys, key=len)
            current_idx = idx

    if current_idx == -1:
        return None, num_room

    return room_name[current_idx], num_room


def lcs(X, Y):
    X = X.replace(' ', '')
    Y = Y.replace(' ', '')
    m = len(X)
    n = len(Y)
    ## declaring the array for storing the dp values
    L = [[None] * (n + 1) for i in range(m + 1)]
    """Following steps build L[m+1][n+1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i - 1] == Y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])

    ## L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]


# ---------- Floor ----------
re_floor = [
    "tang",
    "lau",
    "tam",
    "me",
    "cap 4",
    "tang gac",
    "tang tret",
    "tang lung",
    "tang ham",
    "ban cong",
    "san thuong",
]

floor_name = [
    "tang",
    "tang",
    "tang",
    "tang",
    "tang",
    "gac",
    "tret",
    "lung",
    "ham",
    "ban cong",
    "san thuong",
]


# Normalize floor.
def normalize_floor(text):
    half = 0

    # Remove 'ruoi' text.
    if 'ruoi' in text:
        half = 0.5
        text = re.sub(r"\b{}\b".format('ruoi'), '', text)

    # If the length of arr text is 0, then there is only 1 ground floor.
    text = text.split()
    if len(text) == 0:
        return None, 1

    temp = text[-1]
    text = ' '.join(text[:-1])

    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    text = text + ' ' + temp
    num_arr = [i.group() for i in re.finditer('\d+(\s\.\s\d+)?', text)]
    num_arr = [int(float(i.replace(' ', ''))) for i in num_arr]

    if len(num_arr) > 0:
        num_floor = min(num_arr)
    else:
        num_floor = 1

    lcs_list = list()

    for regex in re_floor:
        lcs_list.append(lcs(regex, text))

##     print(text)
##     print(lcs_list)
    best_match = max(lcs_list)
    if best_match == 0:
        return 'tang', num_floor
    else:
        return floor_name[lcs_list.index(best_match)], num_floor + half


# ---------- District ----------
# Search for the pattern at the beginning of a word like this.
district_alias = [
    r'\bquan', r'\bqan', r'\bqun', r'\bqn', r'\bq ', r'\bq', r'\bdistrict\b',
    r'\bdist', r'\bhuyen', '\bh '
]


# Normalize the district to match the words in the DB.
def normalize_district(text):
    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    # Remove dot symbol.
    text = text.replace('.', ' ')

    # Remove alias in text.
    for alias in district_alias:
        text = re.sub(alias, '', text)

    # Adjust the spacing between words.
    while '  ' in text:
        text = text.replace('  ', ' ')

    # Remove spaces at the beginning and at the end of the string and return.
    return text.strip()


# ---------- Ward ----------
# Search for the pattern at the beginning of a word like this.
ward_alias = [
    r'\bphuong', r'\bphung', r'\bphong', r'\bphg', r'\bpg', r'\bp', r'\bward',
    r'\bxa'
]


# Normalize the ward to match the words in the DB.
def normalize_ward(text):
    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    # Remove dot symbol.
    text = text.replace('.', ' ')

    # Remove alias in text.
    for alias in ward_alias:
        text = re.sub(alias, '', text)

    # Adjust the spacing between words.
    while '  ' in text:
        text = text.replace('  ', ' ')

    # Remove spaces at the beginning and at the end of the string and return.
    return text.strip()


# ---------- Street ----------
# Search for the pattern at the beginning of a word like this.
street_alias = [
    r'\bduong so', r'\bduong', r'\bso', r'\bd', r'\bxom', r'\bthon',
    r'\bstreet'
]


# Normalize the street to match the words in the DB.
def normalize_street(text):
    # Change the text that is a number written in words to a numeric symbol.
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)

    # Remove dot symbol.
    text = text.replace('.', ' ')

    # Remove alias in text.
    for alias in street_alias:
        text = re.sub(alias, '', text)

    # Adjust the spacing between words.
    while '  ' in text:
        text = text.replace('  ', ' ')

    # Remove spaces at the beginning and at the end of the string and return.
    return text.strip()


# ---------- City ----------
# Normalize the city to match the words in the DB.
def normalize_city(text):
    # Remove vietnamese accent.
    text = data_utilities.remove_vietnamese_accent(text)

    # Check text is hcm.
    hcm = ['hcm', 'ho chi minh', 'sai gon', 'sg']
    for i in hcm:
        if i in text: return 'hcm'

    # Check text is hn.
    hn = ['hn', 'ha noi']
    for i in hn:
        if i in text: return 'hn'

    # Remove spaces at the beginning and at the end of the string and return.
    return text.strip()


# ---------- Direction ----------
DIRECTION = [
    'dong', 'nam', 'tay', 'bac', 'dong bac', 'dong nam', 'tay bac', 'tay nam',
    'db', 'dn', 'tb', 'tn', 'khong xac dinh'
]


# Normalize the direction to match the words in the DB.
def normalize_direction(text):
    # List of matching words and percentages [(matched string, percent)].
    text_list = process.extract(text, DIRECTION)

    # Length of first text.
    max_length = len(text_list[0][0])

    # matched percent
    max_score = text_list[0][1]

    # matched string
    res = text_list[0][0]

    # Find the text with the highest percentage of matches.
    for idx, ele in enumerate(text_list):
        # ele:(matched string, percent)
        if ele[1] == max_score:
            if len(ele[0]) > max_length:
                max_length = len(ele[0])
                max_score = ele[1]
                res = ele[0]
        elif ele[1] > max_score:
            max_length = len(ele[0])
            max_score = ele[1]
            res = ele[0]

    if (max_score < 80):
        return ""

    # Replace text to match the words in the DB.
    res = res.replace('dong', 'd')
    res = res.replace('tay', 't')
    res = res.replace('nam', 'n')
    res = res.replace('bac', 'b')
    res = res.replace('khong xac dinh', 'kxd')
    res = res.replace(' ', '')
    return res


# ---------- Position ----------
POSITION = [
    'hem', 'hxh', 'ngo', 'mat tien', 'mat pho', 'mat duong', 'mt', 'mp', 'md'
]

POSITION_NAME = [
    'hem', 'hem', 'hem', 'mat tien', 'mat tien', 'mat tien', 'mat tien',
    'mat tien', 'mat tien'
]

POSITION_INDEX = {w: i for i, w in enumerate(POSITION)}


# Normalize the position to match the words in the DB.
def normalize_position(pos):
    res, score = process.extractOne(pos, POSITION)

    if score < 60:
        return ''

    return POSITION_NAME[POSITION_INDEX[res]]


# ---------- Usage ----------
USAGE = [
    "kinh doanh", "o", "cho thue", "van phong", "cong ty", "dau tu", "spa",
    "lam van phong", "buon ban", "khach san", "mo van phong", "can ho dich vu",
    "nha hang", "showroom", "kd", "shop", "thue", "cty", "ngan hang",
    "shop thoi trang", "cafe", "cua hang", "quan an", "mua ban",
    "kinh doanh online", "truong hoc", "tham my vien", "thoi trang",
    "tru so cong ty", "vp", "can ho", "nha khoa", "cao oc", "phong kham",
    "ban lai", "lam vp", "trung tam dao tao", "tra sua", "xay cao oc",
    "van phong dai dien", "xay khach san", "ca phe", "sieu thi",
    "ban hang online", "xay tro", "quan cafe", "mo vp", "salon toc",
    "trung tam anh ngu", "xay moi", "chdv", "nail",
    "cong ty chuyen phat nhanh", "phong mach", "kd online", "dinh cu",
    "mo cong ty", "mo spa", "online", "lam spa", "trung tam ngoai ngu",
    "ban online", "an uong", "dich vu", "phong tro", "kd nha hang", "toa nha",
    "mo vpct", "xay dung", "tham my", "coffee", "nha xuong", "sieu thi mini",
    "day hoc", "quan nhau", "nha tre", "xay biet thu", "nha thuoc", "lop hoc",
    "salon", "nghi duong", "my pham", "xuong may", "nha tro", "kho",
    "noi that", "vpcty", "xay phong tro", "lam showroom", "quan ca phe",
    "karaoke", "xay nha tro", "lam kho", "xay van phong", "tiem toc",
    "villa biet thu", "studio", "shop online", "kho xuong", "lam vpct",
    "xay nha", "xay can ho dich vu", "tap hoa", "lam van phong cty",
    "sinh song", "vpct", "toa nha van phong", "mo shop", "in theu", "ks",
    "lam vpcty", "benh vien", "nha nghi", "lam cong ty", "truong hoc quoc te",
    "biet thu", "kdoanh online", "mat bang", "lam nha hang", "phong gym",
    "mo truong", "vp cong ty", "tiem thuoc", "vp cty", "mo cty", "xay chdv",
    "gym", "xay dung cao oc", "nha thuoc tay", "mo vpcty", "ngan hang thue",
    "trung tam thuong mai", "mo showroom", "xay building",
    "kinh doanh khach san", "bar", "shop quan ao", "truong mam non",
    "mo cua hang", "cua hang dien thoai", "lam xuong may", "lop day hoc",
    "mo nha hang", "spa lam dep", "lam an", "building van phong", "chua hang",
    "kinh doanh cafe", "trung tam day hoc", "truong anh ngu",
    "xay dung khach san", "vp - cty", "homestay", "yoga", "can ho dv",
    "lam khach san", "kho chua hang", "kd onl", "mo quan cafe", "xay lai",
    "dinh van phong", "dich vu an uong", "mo quan an", "showroom trung bay",
    "xay o", "shop hoa", "khach thue", "truong tu thuc", "mo phong mach",
    "xay dung van phong", "trung bay san pham", "tiem thuoc tay", "lam may",
    "ban hang onl", "mo quan", "mam non", "san xuat", "lam chdv", "lam cafe",
    "mo van phong cty", "vphong", "cong ty chuyen phat", "kinh doanh spa",
    "xay dung building", "kdbb", "kho hang", "lam tai san", "tiem vang",
    "ao cuoi", "buon ban online", "massage", "show room", "mo truong hoc",
    "o gd", "gdinh kdoanh online", "xay toa nha", "lam cty", "mo phong kham",
    "mo tiem"
]


# Check the matching percentage of text.
def normalize_usage(text):
    # matched_string, percent
    res, score = process.extractOne(text, USAGE)

    if score < 60:
        return ''

    return res


# ---------- Legal ----------
LEGAL = [
    'so do', 'so hong', 'sd', 'sh', 'giay phep xay dung', 'gpxd',
    'giay phep kinh doanh', 'gpkd', 'hop dong mua ban', 'hdmb',
    'giay to hop le', 'gthl', 'khong xac dinh'
]

LEGAL_NAME = [
    'so hong do', 'so hong do', 'so hong do', 'so hong do', 'gpxd', 'gpxd',
    'gpkd', 'gpkd', 'hdmb', 'hdmb', 'gthl', 'gthl', 'kxd'
]

LEGAL_INDEX = {w: i for i, w in enumerate(LEGAL)}


# Normalize the legal to match the words in the DB.
def normalize_legal(legal):
    res, score = process.extractOne(legal, LEGAL)

    if score < 50:
        return ''

    return LEGAL_NAME[LEGAL_INDEX[res]]


# ---------- Real estate type ----------
real_estate_type = [
    'nha', 'dat', 'can ho', 'chung cu', 'biet thu', 'villa', 'phong tro',
    'nha tro', 'phong', 'cua hang', 'shop', 'kiots', 'quan', 'khach san',
    'xuong', 'nha xuong', 'kho', 'van phong', 'mat bang', 'toa nha'
]

real_estate_type_name = [
    'nha', 'dat', 'can ho', 'can ho', 'nha', 'nha', 'phong tro nha tro',
    'phong tro nha tro', 'phong tro nha tro', 'mat bang cua hang shop',
    'mat bang cua hang shop', 'mat bang cua hang shop',
    'mat bang cua hang shop', 'nha', 'nha xuong kho bai dat',
    'nha xuong kho bai dat', 'nha xuong kho bai dat', 'van phong',
    'mat bang cua hang shop', 'van phong'
]

real_estate_type_index = {w: i for i, w in enumerate(real_estate_type)}


# Normalize the real_estate_type to match the words in the DB.
def normalize_real_estate_type(text):
    res, score = process.extractOne(text, real_estate_type)

    if score < 70:
        return ''

    return real_estate_type_name[real_estate_type_index[res]]


# ---------- Transaction ----------
TRANSACTION = ['mua', 'ban', 'cho thue', 'can thue', 'sang nhuong', 'can tim']

TRANSACTION_NAME = ['mua', 'ban', 'thue', 'thue', 'ban', 'tim']

TRANSACTION_INDEX = {w: i for i, w in enumerate(TRANSACTION)}


# Normalize the transaction to match the words in the DB.
def normalize_transaction(trans):
    # matched_string, percent
    res, score = process.extractOne(trans, TRANSACTION)

    if score < 50:
        return ''

    return TRANSACTION_NAME[TRANSACTION_INDEX[res]]


# ---------- Numberic ----------
# Find any character between the brackets that is a digit. Remove non-numeric characters.
def normalize_numeric(text):
    text = re.sub(r'[^0-9]', '', text)
    return int(text) if text else 0


normalize("Không xác định", "legal")

# Haven't been able to normalize cases like 1000000000 VND.