import random
import time

import phonenumbers

from src.common.logger import logger
from src.domain.dtos.otp_service_response import OTPServiceResponse


class VirtualPhoneGenerator:
    def __init__(self):
        # Danh sách mã vùng điện thoại của các quốc gia
        # key: mã quốc gia (viết thường), value: tuple (mã vùng quốc tế, độ dài số)
        self.country_formats = {
            'vn': ('+849', 8),  # Việt Nam: Đầu số di động 09xx
            'us': ('+1212', 7),  # Mỹ: New York Area Code
            'au': ('+614', 8),  # Úc: Mobile prefix
            'gb': ('+447', 9),  # Anh: Mobile prefix
            'de': ('+491', 9),  # Đức: Mobile prefix
            'ca': ('+1416', 7),  # Canada: Toronto Area Code
            'fr': ('+336', 8),  # Pháp: Mobile prefix
            'jp': ('+8190', 8),  # Nhật Bản: Mobile prefix
            'kr': ('+8210', 8),  # Hàn Quốc: Mobile prefix
            'cn': ('+8613', 9),  # Trung Quốc: Mobile prefix
            'in': ('+919', 9),  # Ấn Độ: Mobile prefix
            'ru': ('+79', 9),  # Nga: Mobile prefix
            'br': ('+5511', 9),  # Brazil: Sao Paulo Area Code
            'mx': ('+5255', 8),  # Mexico: Mexico City Area Code
            'es': ('+346', 8),  # Tây Ban Nha: Mobile prefix
            'it': ('+393', 9),  # Ý: Mobile prefix
            'nl': ('+316', 8),  # Hà Lan: Mobile prefix
            'se': ('+467', 8),  # Thụy Điển: Mobile prefix
            'no': ('+474', 7),  # Na Uy: Mobile prefix
            'fi': ('+3584', 8),  # Phần Lan: Mobile prefix
            'pl': ('+485', 8),  # Ba Lan: Mobile prefix
            'eg': ('+201', 9),  # Ai Cập: Mobile prefix
            'za': ('+278', 8),  # Nam Phi: Mobile prefix
            'ar': ('+549', 10),  # Argentina: Mobile prefix
            'cl': ('+569', 8),  # Chile: Mobile prefix
            'co': ('+573', 9),  # Colombia: Mobile prefix
            'pe': ('+519', 8),  # Peru: Mobile prefix
            'id': ('+628', 9),  # Indonesia: Mobile prefix
            'my': ('+601', 8),  # Malaysia: Mobile prefix
            'th': ('+668', 8),  # Thái Lan: Mobile prefix
            'ph': ('+639', 9),  # Philippines: Mobile prefix
            'sg': ('+659', 7),  # Singapore: Mobile prefix
            'nz': ('+642', 7),  # New Zealand: Mobile prefix
            'pk': ('+923', 9),  # Pakistan: Mobile prefix
            'bd': ('+8801', 9),  # Bangladesh: Mobile prefix
            'ng': ('+2348', 9),  # Nigeria: Mobile prefix
            'gh': ('+2332', 8),  # Ghana: Mobile prefix
            'ke': ('+2547', 8),  # Kenya: Mobile prefix
            'sa': ('+9665', 8),  # Ả Rập Xê Út: Mobile prefix
            'ae': ('+9715', 8),  # UAE: Mobile prefix
            'af': ('+937', 8),  # Afghanistan: Mobile prefix
            'al': ('+3556', 8),  # Albania: Mobile prefix
            'dz': ('+2137', 8),  # Algeria: Mobile prefix
            'ad': ('+376', 6),  # Andorra: Không có đầu số phổ biến
            'ao': ('+2449', 8),  # Angola: Mobile prefix
            'ag': ('+12687', 6),  # Antigua và Barbuda: Mobile prefix
            'am': ('+3749', 7),  # Armenia: Mobile prefix
            'at': ('+436', 9),  # Áo: Mobile prefix
            'az': ('+9945', 8),  # Azerbaijan: Mobile prefix
            'bh': ('+9733', 7),  # Bahrain: Mobile prefix
            'bs': ('+12423', 6),  # Bahamas: Mobile prefix
            'bb': ('+12462', 6),  # Barbados: Mobile prefix
            'by': ('+37529', 7),  # Belarus: Mobile prefix
            'be': ('+324', 8),  # Bỉ: Mobile prefix
            'bz': ('+5016', 6),  # Belize: Mobile prefix
            'bj': ('+2296', 7),  # Benin: Mobile prefix
            'bt': ('+9751', 7),  # Bhutan: Mobile prefix
            'bo': ('+5917', 7),  # Bolivia: Mobile prefix
            'ba': ('+3876', 7),  # Bosnia và Herzegovina: Mobile prefix
            'bw': ('+2677', 6),  # Botswana: Mobile prefix
            'bn': ('+6738', 6),  # Brunei: Mobile prefix
            'bg': ('+3598', 8),  # Bulgaria: Mobile prefix
            'bf': ('+2267', 7),  # Burkina Faso: Mobile prefix
            'bi': ('+2577', 7),  # Burundi: Mobile prefix
            'kh': ('+8551', 7),  # Campuchia: Mobile prefix
            'cm': ('+2376', 8),  # Cameroon: Mobile prefix
            'cv': ('+2389', 6),  # Cape Verde: Mobile prefix
            'cf': ('+2367', 7),  # Cộng hòa Trung Phi: Mobile prefix
            'td': ('+2356', 7),  # Chad: Mobile prefix
            'cy': ('+3579', 7),  # Síp: Mobile prefix
            'cz': ('+4206', 8),  # Cộng hòa Séc: Mobile prefix
            'cd': ('+2438', 8),  # Cộng hòa Dân chủ Congo: Mobile prefix
            'dk': ('+452', 7),  # Đan Mạch: Mobile prefix
            'dj': ('+2537', 7),  # Djibouti: Mobile prefix
            'dm': ('+17676', 6),  # Dominica: Mobile prefix
            'do': ('+18098', 9),  # Cộng hòa Dominica: Mobile prefix
            'ec': ('+5939', 8),  # Ecuador: Mobile prefix
            'sv': ('+5037', 7),  # El Salvador: Mobile prefix
            'gq': ('+2402', 8),  # Guinea Xích đạo: Mobile prefix
            'er': ('+2911', 6),  # Eritrea: Mobile prefix
            'ee': ('+3725', 7),  # Estonia: Mobile prefix
            'et': ('+2519', 8),  # Ethiopia: Mobile prefix
            'fj': ('+6799', 6),  # Fiji: Mobile prefix
            'ga': ('+2416', 6),  # Gabon: Mobile prefix
            'gm': ('+2207', 6),  # Gambia: Mobile prefix
            'ge': ('+9955', 8),  # Gruzia: Mobile prefix
            'gr': ('+306', 9),  # Hy Lạp: Mobile prefix
            'gl': ('+299', 6),  # Greenland: Không có đầu số phổ biến
            'gd': ('+14734', 6),  # Grenada: Mobile prefix
            'gt': ('+5024', 7),  # Guatemala: Mobile prefix
            'gn': ('+2246', 8),  # Guinea: Mobile prefix
            'gw': ('+2459', 6),  # Guinea-Bissau: Mobile prefix
            'gy': ('+5926', 6),  # Guyana: Mobile prefix
            'ht': ('+5093', 7),  # Haiti: Mobile prefix
            'hn': ('+5043', 7),  # Honduras: Mobile prefix
            'hu': ('+3620', 7),  # Hungary: Mobile prefix
            'is': ('+3546', 6),  # Iceland: Mobile prefix
            'ir': ('+989', 9),  # Iran: Mobile prefix
            'iq': ('+9647', 9),  # Iraq: Mobile prefix
            'ie': ('+3538', 8),  # Ireland: Mobile prefix
            'il': ('+9725', 8),  # Israel: Mobile prefix
            'ci': ('+2250', 9),  # Bờ Biển Ngà: Mobile prefix
            'jm': ('+18763', 6),  # Jamaica: Mobile prefix
            'jo': ('+9627', 8),  # Jordan: Mobile prefix
            'kz': ('+77', 9),  # Kazakhstan: Mobile prefix
            'kw': ('+9656', 7),  # Kuwait: Mobile prefix
            'kg': ('+9967', 8),  # Kyrgyzstan: Mobile prefix
            'la': ('+85620', 8),  # Lào: Mobile prefix
            'lv': ('+3712', 7),  # Latvia: Mobile prefix
            'lb': ('+9617', 7),  # Lebanon: Mobile prefix
            'ls': ('+2665', 7),  # Lesotho: Mobile prefix
            'lr': ('+2317', 6),  # Liberia: Mobile prefix
            'ly': ('+2189', 8),  # Libya: Mobile prefix
            'li': ('+4237', 6),  # Liechtenstein: Mobile prefix
            'lt': ('+3706', 7),  # Lithuania: Mobile prefix
            'lu': ('+3526', 8),  # Luxembourg: Mobile prefix
            'mk': ('+3897', 7),  # Bắc Macedonia: Mobile prefix
            'mg': ('+2613', 8),  # Madagascar: Mobile prefix
            'mw': ('+2659', 8),  # Malawi: Mobile prefix
            'mv': ('+9607', 6),  # Maldives: Mobile prefix
            'ml': ('+2236', 7),  # Mali: Mobile prefix
            'mt': ('+3569', 7),  # Malta: Mobile prefix
            'mr': ('+2224', 7),  # Mauritania: Mobile prefix
            'mu': ('+2305', 7),  # Mauritius: Mobile prefix
            'md': ('+3736', 7),  # Moldova: Mobile prefix
            'mc': ('+377', 8),  # Monaco: Không có đầu số phổ biến
            'mn': ('+9769', 7),  # Mông Cổ: Mobile prefix
            'me': ('+3826', 7),  # Montenegro: Mobile prefix
            'ma': ('+2126', 8),  # Morocco: Mobile prefix
            'mz': ('+2588', 8),  # Mozambique: Mobile prefix
            'mm': ('+959', 8),  # Myanmar: Mobile prefix
            'na': ('+2648', 8),  # Namibia: Mobile prefix
            'np': ('+97798', 8),  # Nepal: Mobile prefix
            'ni': ('+5058', 7),  # Nicaragua: Mobile prefix
            'ne': ('+2279', 7),  # Niger: Mobile prefix
            'om': ('+9689', 7),  # Oman: Mobile prefix
            'pa': ('+5076', 7),  # Panama: Mobile prefix
            'pg': ('+6757', 7),  # Papua New Guinea: Mobile prefix
            'py': ('+5959', 8),  # Paraguay: Mobile prefix
            'qa': ('+9745', 7),  # Qatar: Mobile prefix
            'ro': ('+407', 8),  # Romania: Mobile prefix
            'rw': ('+2507', 8),  # Rwanda: Mobile prefix
            'kn': ('+18697', 6),  # Saint Kitts và Nevis: Mobile prefix
            'lc': ('+17587', 6),  # Saint Lucia: Mobile prefix
            'vc': ('+17845', 6),  # Saint Vincent và Grenadines: Mobile prefix
            'ws': ('+6857', 6),  # Samoa: Mobile prefix
            'sm': ('+3786', 9),  # San Marino: Mobile prefix
            'st': ('+2399', 6),  # São Tomé và Príncipe: Mobile prefix
            'sn': ('+2217', 8),  # Senegal: Mobile prefix
            'rs': ('+3816', 8),  # Serbia: Mobile prefix
            'sc': ('+2482', 6),  # Seychelles: Mobile prefix
            'sl': ('+2327', 7),  # Sierra Leone: Mobile prefix
            'sk': ('+4219', 8),  # Slovakia: Mobile prefix
            'si': ('+3864', 7),  # Slovenia: Mobile prefix
            'sb': ('+6777', 6),  # Quần đảo Solomon: Mobile prefix
            'so': ('+2526', 7),  # Somalia: Mobile prefix
            'lk': ('+947', 8),  # Sri Lanka: Mobile prefix
            'sr': ('+5978', 6),  # Suriname: Mobile prefix
            'sz': ('+2687', 7),  # Eswatini: Mobile prefix
            'ch': ('+417', 8),  # Thụy Sĩ: Mobile prefix
            'sy': ('+9639', 8),  # Syria: Mobile prefix
            'tw': ('+8869', 8),  # Đài Loan: Mobile prefix
            'tj': ('+9929', 8),  # Tajikistan: Mobile prefix
            'tz': ('+2557', 8),  # Tanzania: Mobile prefix
            'tg': ('+2289', 7),  # Togo: Mobile prefix
            'to': ('+6768', 6),  # Tonga: Mobile prefix
            'tt': ('+18683', 6),  # Trinidad và Tobago: Mobile prefix
            'tn': ('+2162', 7),  # Tunisia: Mobile prefix
            'tr': ('+905', 9),  # Thổ Nhĩ Kỳ: Mobile prefix
            'tm': ('+9936', 7),  # Turkmenistan: Mobile prefix
            'ug': ('+2567', 8),  # Uganda: Mobile prefix
            'ua': ('+3809', 8),  # Ukraine: Mobile prefix
            'uy': ('+5989', 7),  # Uruguay: Mobile prefix
            'uz': ('+9989', 8),  # Uzbekistan: Mobile prefix
            'vu': ('+6787', 6),  # Vanuatu: Mobile prefix
            've': ('+584', 9),  # Venezuela: Mobile prefix
            'ye': ('+9677', 8),  # Yemen: Mobile prefix
            'zm': ('+2609', 8),  # Zambia: Mobile prefix
            'zw': ('+2637', 8),  # Zimbabwe: Mobile prefix
        }

    def _generate_generic_number(self, country_code: str) -> OTPServiceResponse:
        country_code_lower = country_code.lower()
        if country_code_lower not in self.country_formats:
            country_code_lower = "us"

        prefix, length = self.country_formats[country_code_lower]
        region_code = country_code_lower.upper()

        start_time = time.time()
        while time.time() - start_time < 30:
            # Tạo các chữ số còn lại một cách ngẫu nhiên
            remaining_digits = ''.join(str(random.randint(0, 9)) for _ in range(length))
            new_contact = f"{prefix}{remaining_digits}"

            try:
                # Phân tích số điện thoại để kiểm tra
                parsed_number = phonenumbers.parse(new_contact, region=region_code)

                # Kiểm tra xem số có hợp lệ hay không.
                # Nếu hợp lệ thì thoát vòng lặp và trả về số
                if phonenumbers.is_valid_number(parsed_number):
                    return OTPServiceResponse(id=new_contact, contact=new_contact, additional_value=new_contact)
            except phonenumbers.NumberParseException:
                # Bỏ qua các số không thể phân tích được
                pass

        logger.error(f"Không lấy được số điện thoại hợp lệ cho mã quốc gia: {region_code} - Prefix: {prefix} - Length: {length}")

        # fallback sang số us
        return self._generate_generic_number('US')

    def create(self, country_code: str) -> OTPServiceResponse:
        return self._generate_generic_number(country_code)
