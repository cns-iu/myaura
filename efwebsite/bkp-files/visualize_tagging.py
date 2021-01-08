# -*- coding: utf-8 -*-
"""
Created on Sat May 25 14:23:16 2019

@author: Sikander
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pickle
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy
import networkx as nx
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib as mpl
from matplotlib import cm

#PRELIMINARY
created = {2005: 5916, 2006: 7934, 2007: 11402, 2008: 11176, 
           2009: 14611, 2010: 18027, 2011: 14872, 2012: 7382, 2013: 5519, 
           2014: 10264, 2015: 10311, 2016: 8254}

dob = {1970: 57, 1971: 50, 1972: 42, 1973: 46, 1974: 47, 1975: 64, 1976: 49, 
       1977: 52, 1978: 54, 1979: 61, 1980: 64, 1981: 61, 1982: 77, 1983: 70, 
       1984: 71, 1985: 88, 1986: 83, 1987: 75, 1988: 79, 1989: 82, 1990: 98, 
       1991: 69, 1992: 79, 1993: 59, 1994: 62, 1995: 59, 1996: 42, 1997: 37, 
       1998: 31, 1999: 24, 2000: 15, 2001: 14, 2002: 4, 2003: 7, 2004: 2, 
       2005: 3, 2006: 2, 2007: 6, 2008: 3, 2009: 3, 2010: 2, 2011: 2, 2012: 3, 
       2013: 7}

eptype = {'A Person Living with Epilepsy': 1693,
        'A Parent of a Child with Epilepsy': 329, 
        'A Family Member or Caregiver': 143, 'Healthcare Professional': 83}

control = {'Not controlled': 982, 'Controlled': 799}

country = {'BD': 4, 'FR': 1, 'DK': 1, 'MZ': 1, 'HR': 1, 'TR': 5, 'BO': 1, 
           'JP': 1, 'BT': 1, 'CH': 3, 'DZ': 3, 'MK': 1, 'BR': 3, 'CO': 2, 
           'GR': 2, 'PR': 3, 'RU': 1, 'LB': 1, 'PT': 3, 'NO': 6, 'TT': 1, 
           'AF': 1, 'DE': 3, 'NG': 3, 'TN': 1, 'EE': 1, 'NZ': 14, 'LU': 1, 
           'LR': 1, 'LS': 1, 'TH': 2, 'PE': 1, 'NP': 5, 'PK': 10, 'AT': 1, 
           'RO': 2, 'EG': 3, 'PL': 1, 'EC': 1, 'BE': 1, 'GT': 1, 'AE': 4, 
           'VE': 2, 'CM': 1, 'CL': 1, 'IQ': 1, 'BH': 1, 'CA': 88, 'IR': 2, 
           'ZA': 16, 'VN': 6, 'AL': 1, 'GG': 1, 'CY': 2, 'AR': 4, 'AU': 32, 
           'IL': 3, 'IN': 53, 'BA': 1, 'NL': 3, 'ID': 2, 'IE': 5, 'PH': 15, 
           'ES': 4, 'GH': 1, 'MA': 2, 'KE': 2, 'SG': 2, 'ZM': 1, 'GE': 2, 
           'QA': 2, 'MT': 1, 'SI': 1, 'BW': 2, 'TZ': 2, 'IT': 1, 
           'HN': 1, 'UG': 1, 'SD': 2, 'UA': 4, 'MX': 8, 'SE': 3, 'GB': 124}

#PRELIMINARY 2

us_states = {'WA': 45, 'DE': 13, 'DC': 9, 'WI': 33, 'WV': 13, 'HI': 5, 'FL': 110, 
             'WY': 3, 'NH': 11, 'NJ': 51, 'NM': 16, 'TX': 179, 'LA': 30, 'NC': 54, 
             'ND': 2, 'NE': 10, 'TN': 49, 'NY': 107, 'PA': 77, 'AK': 4, 'NV': 20, 
             'VA': 55, 'CO': 53, 'CA': 184, 'AL': 30, 'AR': 15, 'VT': 3, 'IL': 81, 
             'GA': 48, 'IN': 31, 'IA': 18, 'OK': 24, 'AZ': 43, 'ID': 14, 'CT': 22, 
             'ME': 11, 'MD': 44, 'MA': 53, 'OH': 65, 'UT': 21, 'MO': 37, 'MN': 26, 
             'MI': 50, 'RI': 10, 'KS': 16, 'MT': 12, 'MS': 14, 'PR': 4, 'SC': 41, 
             'KY': 20, 'OR': 29, 'SD': 8}
us_st_pop = {'WA': 7.54, 'DE': 0.967, 'DC': 0.702, 'WI': 5.81, 'WV': 1.81, 'HI': 1.42,
             'FL': 21.3, 'WY': 0.578, 'NH': 1.36, 'NJ': 8.91, 'NM': 2.1, 'TX': 27.8,
             'LA': 4.66, 'NC': 10.4, 'ND': 0.76, 'NE': 3.03, 'TN': 6.77, 'NY': 19.5,
             'PA': 12.8, 'AK': 0.737, 'NV': 3.03, 'VA': 8.52, 'CO': 5.7, 'CA': 39.6, 
             'AL': 4.89, 'AR': 3.01, 'VT': 0.626, 'IL': 12.7, 'GA': 10.5, 'IN': 6.69,
             'IA': 3.12, 'OK': 3.94, 'AZ': 7.17, 'ID': 1.75, 'CT': 3.57, 'ME': 1.34,
             'MD': 6.04, 'MA': 6.9, 'OH': 11.7, 'UT': 3.16, 'MO': 6.13, 'MN': 5.61,
             'MI': 10.0, 'RI': 1.06, 'KS': 2.91, 'MT': 1.06, 'MS': 2.99, 'PR': 3.2,
             'SC': 5.08, 'KY': 4.47, 'OR': 4.19, 'SD': 0.882}
norm_state_demo = {'WA': 5.968169761273209,'DE': 13.44364012409514,'DC': 12.820512820512821,
                   'WI': 5.679862306368331, 'WV': 7.18232044198895, 'HI': 3.5211267605633805,
                   'FL': 5.164319248826291, 'WY': 5.190311418685122, 'NH': 8.088235294117647,
                   'NJ': 5.723905723905724, 'NM': 7.619047619047619, 'TX': 6.438848920863309,
                   'LA': 6.437768240343347, 'NC': 5.1923076923076925, 'ND': 2.6315789473684212,
                   'NE': 3.3003300330033007, 'TN': 7.237813884785821, 'NY': 5.487179487179487,
                   'PA': 6.015625, 'AK': 5.4274084124830395, 'NV': 6.6006600660066015, 'VA': 6.455399061032864, 
                   'CO': 9.298245614035087, 'CA': 4.646464646464646, 'AL': 6.134969325153374, 'AR': 4.983388704318937,
                   'VT': 4.792332268370607, 'IL': 6.377952755905512, 'GA': 4.571428571428571, 'IN': 4.633781763826606, 
                   'IA': 5.769230769230769, 'OK': 6.091370558375635, 'AZ': 5.99721059972106, 'ID': 8.0, 
                   'CT': 6.162464985994398, 'ME': 8.208955223880597, 'MD': 7.28476821192053, 'MA': 7.6811594202898545, 
                   'OH': 5.555555555555556, 'UT': 6.6455696202531644, 'MO': 6.035889070146819, 'MN': 4.634581105169341, 
                   'MI': 5.0, 'RI': 9.433962264150942, 'KS': 5.498281786941581, 'MT': 11.320754716981131, 'MS': 4.682274247491638, 
                   'PR': 1.25, 'SC': 8.070866141732283, 'KY': 4.47427293064877, 'OR': 6.921241050119331, 'SD': 9.070294784580499}

uk_countries = {'England': 41, 'Northern Ireland': 2, 'Scotland': 11, 'Wales': 5}

ca_provinces = {'ON': 32, 'AB': 9, 'NL': 1, 'MB': 5, 'NB': 2, 'BC': 16, 'SK': 5, 'QC': 3, 'NS': 2}

in_states = {'Telangana': 5, 'Karnataka': 5, 'Haryana': 2, 'Andhra Pradesh': 2, 
             'Gujarat': 2, 'Kerala': 1, 'Uttrakhand': 1, 'Maharashtra': 7, 
             'Tamil Nadu': 5, 'Delhi': 7, 'Rajasthan': 2, 'West Bengal': 2, 
             'Jammu & Kashmir': 2, 'Uttar Pradesh': 2, 'Madhya Pradesh': 1, 
             'Chandigarh': 1, 'Assam': 1, 'Punjab': 1}

au_states = {'VIC': 7, 'WA': 2, 'TAS': 1, 'ACT': 1, 'QLD': 7, 'SA': 2, 'NSW': 3}

#LEVEL OF ENGAGEMENT
num_posts = {1: 12314, 2: 4009, 3: 1963, 4: 1114, 5: 679, 6: 476, 7: 369, 8: 273, 
             9: 218, 10: 147, 11: 133, 12: 105, 13: 88, 14: 87, 15: 76, 16: 71, 
             17: 50, 18: 55, 19: 31, 20: 46, 21: 30, 22: 28, 23: 32, 24: 32, 25: 20, 
             26: 29, 27: 20, 28: 18, 29: 16, 30: 15, 31: 19, 32: 11, 33: 14, 34: 10, 
             35: 5, 36: 12, 37: 5,38: 10, 39: 7, 40: 8, 41: 11, 
             42: 7, 43: 5, 44: 5, 45: 4, 46: 5, 47: 4, 48: 10, 49: 7, 50: 5, 51: 5, 
             52: 4, 53: 3, 54: 7, 55: 1,
             56: 2, 57: 3, 58: 9, 59: 4, 60: 2, 61: 3, 62: 3, 63: 1, 64: 4, 
             65: 4, 66: 3, 67: 2, 68: 1, 69: 4, 70: 5, 71: 4, 72: 4, 73: 3, 74: 1, 
             75: 1, 76: 5, 77: 1, 78: 1, 79: 1, 80: 2, 81: 4, 82: 1, 83: 1, 84: 2, 
             85: 5, 86: 3, 87: 1, 88: 1, 89: 1, 90: 2, 93: 1, 94: 2, 95: 2, 96: 1, 
             97: 2, 99: 2, 100: 1, 101: 1, 103: 2, 104: 1, 105: 2, 106: 1, 108: 3, 
             109: 1, 111: 3, 113: 3, 116: 1, 117: 1, 118: 1, 119: 1, 122: 3, 124: 1, 
             125: 1, 129: 1, 131: 1, 132: 1,  133: 2, 137: 3, 140: 3, 141: 1, 143: 1, 
             144: 3, 145: 2, 148: 1,  152: 1, 154: 1, 158: 1, 160: 1, 162: 1, 169: 1, 
             172: 1, 175: 1, 183: 1, 184: 1, 187: 1,  193: 1, 194: 1, 198: 1, 200: 1, 
             201: 1,  205: 1, 211: 1, 215: 1, 217: 1, 220: 1, 221: 1, 229: 1, 233: 1, 
             253: 1, 255: 1, 259: 1, 268: 1, 269: 1, 271: 1, 277: 2, 278: 1,  283: 1, 
             284: 1, 285: 1, 336: 1, 349: 1, 350: 1, 353: 1, 360: 1,  395: 1, 399: 1, 
             413: 1, 457: 1, 568: 1, 605: 1, 655: 1, 692: 1,  698: 1, 713: 1, 734: 1, 
             918: 1,  1022: 1, 1034: 1, 1091: 1, 1195: 1, 1528: 1, 1609: 1, 4284: 1}

num_chats = {1: 329, 2: 133, 3: 66, 4: 69, 5: 53, 6: 56, 7: 35, 8: 37, 9: 30, 10: 31, 
             11: 29, 12: 24, 13: 20, 14: 28, 15: 22, 16: 30, 17: 27, 18: 26, 19: 20, 
             20: 28, 21: 22, 22: 22, 23: 22, 24: 13, 25: 18, 26: 22, 27: 15, 28: 21, 
             29: 16, 30: 16, 31: 10, 32: 12, 33: 15, 34: 12, 35: 15, 36: 12, 37: 12, 
             38: 11, 39: 12, 40: 11, 41: 6, 42: 8, 43: 10, 44: 7, 45: 11, 46: 5, 
             47: 6, 48: 6, 49: 8, 50: 7, 51: 8, 52: 6, 53: 2, 54: 4, 55: 4, 56: 4, 
             57: 3, 58: 6, 59: 4, 60: 4, 61: 7, 62: 2, 63: 6, 64: 4, 65: 9, 66: 4, 
             67: 4, 68: 4, 69: 1, 70: 5, 71: 2, 72: 6, 73: 4, 74: 1, 75: 6, 76: 3}

#MEMBER TYPE ANALYSIS

created_PLE = {2016: 239, 2005: 7, 2006: 4, 2007: 19, 2008: 23, 2009: 31, 
               2010: 42, 2011: 51, 2012: 48, 2013: 59, 2014: 485, 2015: 685}
created_PCE = {2016: 43, 2009: 4, 2010: 3, 2011: 9, 2012: 2, 2013: 10, 2014: 102, 2015: 156}
created_FMC = {2016: 20, 2008: 2, 2009: 1, 2010: 2, 2011: 2, 2012: 2, 2013: 1, 2014: 42, 2015: 71}
created_HP = {2016: 14, 2008: 1, 2009: 4, 2011: 1, 2012: 1, 2013: 3, 2014: 19, 2015: 40}

dob_PLE = {1970: 35, 1971: 34, 1972: 27, 1973: 27, 1974: 32, 1975: 44, 1976: 33, 
           1977: 24, 1978: 32, 1979: 36, 1980: 36, 1981: 38, 1982: 51, 1983: 52, 
           1984: 37, 1985: 56, 1986: 63, 1987: 46, 1988: 57, 1989: 50, 1990: 55, 
           1991: 47, 1992: 58, 1993: 47, 1994: 44, 1995: 41, 1996: 29, 1997: 28, 
           1998: 23, 1999: 20, 2000: 5, 2001: 10, 2002: 2, 2006: 2, 2007: 2, 
           2009: 1, 2012: 1, 2014: 41, 2015: 44, 2016: 15}
dob_PCE = {1970: 11, 1971: 4, 1972: 8, 1973: 10, 1974: 7, 1975: 12, 1976: 8, 
           1977: 15, 1978: 12, 1979: 11, 1980: 9, 1981: 6, 1982: 12, 1983: 7, 
           1984: 8, 1985: 9, 1986: 5, 1987: 9, 1988: 5, 1989: 7, 1990: 6, 1991: 5, 
           1992: 3, 1993: 2, 1994: 1, 1995: 4, 1996: 1, 1999: 1, 2001: 1, 2002: 1, 
           2003: 5, 2004: 1, 2005: 3, 2007: 2, 2008: 3, 2009: 1, 2010: 2, 2011: 2, 
           2012: 2, 2013: 2, 2014: 16, 2015: 21, 2016: 7}
dob_FMC = {1970: 3, 1971: 3, 1972: 1, 1973: 2, 1974: 2, 1975: 1, 1976: 1, 1977: 3, 
           1978: 1, 1979: 5, 1981: 1, 1982: 2, 1983: 3, 1985: 4, 1986: 2, 1987: 2, 
           1988: 4, 1989: 5, 1990: 8, 1991: 5, 1992: 4, 1993: 2, 1994: 6, 1996: 1, 
           1999: 1, 2000: 1, 2003: 1, 2004: 1, 2013: 1, 2014: 7, 2015: 10, 2016: 1}
dob_HP = {1970: 3, 1971: 3, 1972: 1, 1973: 2, 1974: 2, 1975: 1, 1976: 1, 1977: 3, 
          1978: 1, 1979: 5, 1981: 1, 1982: 2, 1983: 3, 1985: 4, 1986: 2, 1987: 2, 
          1988: 4, 1989: 5, 1990: 8, 1991: 5, 1992: 4, 1993: 2, 1994: 6, 1996: 1, 
          1999: 1, 2000: 1, 2003: 1, 2004: 1, 2013: 1, 2014: 7, 2015: 10, 2016: 1}

#TIMELINES
chats_tl_top = np.delete(np.load("chats_tl_top.npy"), -1, 1)
chats_tl_all = np.load("chats_tl_all.npy")
chats_tl_wkly = np.load("chats_tl_wkly.npy")
forums_tl_top = np.delete(np.load("forums_tl_top.npy"), -1, 1)
forums_tl_all = np.load("forums_tl_all.npy")
forums_tl_wkly = np.load("forums_tl_wkly.npy")
chats_range = ['7-2014','8-2014','9-2014','10-2014','11-2014','12-2014','1-2015','2-2015','3-2015']
forums_range = ['2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016']
forums_ticks = [2, 14, 26, 38, 50, 62, 74, 86, 98, 110, 122, 134]

#TOP USERS {uid: #posts/chats}
usrs_chats = {124741: 3159,142931: 3188,206786: 3234, 91813: 3614, 133186: 3632, 102710: 3699,
              74879: 3753, 226796: 3846, 123406: 3906, 103467: 4204, 93147: 4258, 168131: 4631,
              117586: 4719, 153391: 5356, 203441: 5358, 123996: 6112, 87564: 7539, 95416: 7711,
              44294: 10456, 98914: 11613, 188006: 14238, 90109: 17011, 94861: 18854, 23487: 20288,
              214556: 22108, 40886: 45498}
usrs_forums =  {13600: 336,2495: 349,12416: 350,39104: 353, 22834: 360, 15797: 395, 
                70585: 399, 16756: 413, 26464: 457, 33641: 568, 3421: 605, 1837: 655,
                42622: 692, 43851: 698, 10112: 713, 27976: 734, 53211: 918, 13993: 1022,
                2731: 1034, 1998: 1091, 40321: 1195, 51501: 1528, 101498: 1609, 0: 4284}

#FORUM topics
forum_topics = {u'Fundraising and Awareness': 118, u'Products, Resources, Helpful Links': 588, 
                u'Women With Epilepsy': 6309, u'Teens Speak Up! ': 3, u'Insurance Issues': 425, 
                u'Medication Issues': 17723, u'Epilepsy: Insights & Strategies': 178, 
                u'Corner Booth': 3504, u'Living With Epilepsy - Adults': 34304, 
                u'Men With Epilepsy': 947, u'Surgery and Devices': 4124, 
                u'Lennox Gastaut Syndrome': 8, u'Veterans with seizures': 115, 
                u'Family & Friends': 4730, u'Share Your #DareTo Go The Distance Story': 31, 
                u'Parents & Caregivers': 7025, u'Epilepsy.com Help': 1755, u'Athletes vs Epilepsy Goal Posts': 1, 
                u'Epilepsy and College ': 90, u'New to Epilepsy.com': 14876, u'Living With Epilepsy - Youth': 3843, 
                u'Creative Corner': 251, u'Diagnostic Dilemmas and Testing': 5190, u'Complementary Therapies': 1674, 
                u'Teen Zone': 2113, u'My Epilepsy Diary': 674, u'In Memoriam': 7, u'Advocate for Epilepsy': 465, 
                u'Infantile Spasms & Tuberous Sclerosis': 4}

#Tagging results
topics_dct = {'Fundraising and Awareness': 2003194, 'Products, Resources, Helpful Links': 2003130,
				'Women With Epilepsy': 2003119, 'Teens Speak Up!': 2010661, 'Insurance Issues': 2003133,
				'Medication Issues': 2003121, 'Insights & Strategies': 2003197,
				'Share Your #DareTo Go The Distance Story': 2036596, 'Living With Epilepsy - Adults': 2003117,
				'Men With Epilepsy': 2003129, 'Surgery and Devices': 2003122, 'Lennox Gastaut Syndrome': 2008441,
				'Veterans with seizures': 2003180, 'Family & Friends': 2003118, 'Corner Booth': 2003123,
				'Parents & Caregivers': 2003131, 'Epilepsy.com Help': 2003127, 'Athletes vs Epilepsy Goal Posts': 2044536,
				'Epilepsy and College': 2003304, 'New to Epilepsy.com': 2003125, 'Living With Epilepsy - Youth': 2003128,
				'Creative Corner': 2003134, 'Diagnostic Dilemmas and Testing': 2003126, 'Complementary Therapies': 2003124,
				'Teen Zone': 2003120, 'My Epilepsy Diary': 2003228, 'In Memoriam': 2014491, 'Advocate for Epilepsy': 2003132,
				'Infantile Spasms & Tuberous Sclerosis': 2008446}
#{'Topic name': (Mathced posts, Total Posts)}
topics_match = {'Fundraising and Awareness': (77, 118), 'Products, Resources, Helpful Links': (416, 588), 
                'Women With Epilepsy': (5664, 6309), 'Insurance Issues': (273, 425), 'Medication Issues': (15831, 17723), 
                'Share Your #DareTo Go The Distance Story': (24, 31), 'Living With Epilepsy - Adults': (28293, 34304), 
                'Men With Epilepsy': (796, 947), 'Surgery and Devices': (3671, 4124), 'Lennox Gastaut Syndrome': (4, 8), 
                'Veterans with seizures': (94, 115), 'Teens Speak Up!': (2, 3), 'Family & Friends': (3912, 4730), 
                'Epilepsy and College': (64, 90), 'Insights & Strategies': (145, 178), 'Corner Booth': (1667, 3504), 
                'Parents & Caregivers': (6173, 7025), 'Epilepsy.com Help': (1049, 1755), 'Athletes vs Epilepsy Goal Posts': (1, 1), 
                'New to Epilepsy.com': (12978, 14876), 'Living With Epilepsy - Youth': (3345, 3843), 'Creative Corner': (142, 251), 
                'Diagnostic Dilemmas and Testing': (4498, 5190), 'Complementary Therapies': (1421, 1674), 'Teen Zone': (1674, 2113), 
                'My Epilepsy Diary': (525, 674), 'In Memoriam': (7, 7), 'Advocate for Epilepsy': (350, 465), 
                'Infantile Spasms & Tuberous Sclerosis': (4, 4)}

#TAGGING ANALYSIS
matchesperchat = pickle.load(open('tag_analysis/matchesperpost_c.pkl', 'rb'))
matchesperpost = pickle.load(open('tag_analysis/matchesperpost_p.pkl', 'rb'))
matchesperuser_c = pickle.load(open('tag_analysis/matchesperuser_c.pkl', 'rb'))
matchesperuser_p = pickle.load(open('tag_analysis/matchesperuser_p.pkl', 'rb'))
matchpostperuse_c = pickle.load(open('tag_analysis/matchpostsperuser_c.pkl', 'rb'))
matchpostperuse_p = pickle.load(open('tag_analysis/matchpostsperuser_p.pkl', 'rb'))
parents_c = pickle.load(open('tag_analysis/parents_c.pkl', 'rb'))
parents_p = pickle.load(open('tag_analysis/parents_p.pkl', 'rb'))
types_c = pickle.load(open('tag_analysis/types_c.pkl', 'rb'))
types_p = pickle.load(open('tag_analysis/types_p.pkl', 'rb'))

#COMENTIONS
double_menchies = pickle.load(open('double_mentions.pkl', 'rb'))

#TF_IDF
topic_number_dct = pickle.load(open('TF-IDF/topic_number_dct.pkl', 'rb'))

def barchart(dct, title, yscale, xtrot=None):
    plt.figure()
    plt.bar(dct.keys(), dct.values(), align='center', orientation='h')
    if xtrot:
        plt.xticks(rotation='vertical')
    plt.ylabel("Count", fontsize=18)
    plt.yscale(yscale)
    
    plt.title(title, fontsize=24)
    #plt.gcf().subplots_adjust(bottom=0.25) #May not need
    plt.show()

def horiz_bar(dct, title, xlabel, ylabel):
    y_pos = np.arange(len(dct))
    plt.figure()
    vals = [v for v in dct.values()]
    keys = [k for k in dct.keys()]
    plt.barh(y_pos, vals, align='center')
    plt.yticks(y_pos, keys)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
    
def histo(dct, bins, title, yscale):
    plt.figure()
    dat = []
    for k in dct:
        dat += dct[k]*[k]
    plt.hist(dat, bins=bins)
    plt.yscale(yscale)
    plt.title(title, fontsize=24)
    plt.ylabel("Count", fontsize=18)
    plt.show()
    
def samplesize(dct):
    size = 0
    for k in dct:
        size += dct[k]
    return size
    
def tally(dct, key):
    if key in dct:
        dct[key] += 1
    else:
        dct[key] = 1

def sortkeys(dct, order=False):
    nd = dict()
    for key in sorted(dct.keys(), reverse=order):
        nd[key] = dct[key]
    return nd

def sortvals(dct, order=False):
    nd = dict()
    for k in sorted(dct, key=dct.get, reverse=order):
        nd[k] = dct[k]
    return nd

def topitems(dct, top):
    count = 0
    nd = dict()
    for key in dct.keys():
        count += 1
        if count <= top:
            nd[key] = dct[key]
    return nd

def monthsInRange(beg, end):
    result = []
    beg = datetime.strptime(beg, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    while beg < end:
        result.append(str(beg.month) + '-' + str(beg.year))
        beg += relativedelta(months=1)
    result.append(str(end.month) + '-' + str(end.year))
    return result

def visualizeTimeline(tl_arr, name, usrnum, clim, labels, ticks=None):
    plasma_cm = cm.get_cmap('plasma', 512)
    newcmp = ListedColormap(plasma_cm(np.linspace(0.25, 1, 1000)))
    plt.matshow(tl_arr, cmap=newcmp, aspect="auto")
    plt.clim(0, clim)
    plt.colorbar().set_label(label=name + ' per month', size=18)
    plt.title("Visualization of Top " + usrnum + " Timelines", fontsize=24)
    if ticks:
        plt.xticks(ticks, labels)
    else:
        plt.xticks(range(len(labels)), labels)
    plt.xlabel('Month', fontsize=16)
    plt.ylabel('Users', fontsize=16)
    plt.show()
    
def tot_usage(tl_arr, name, labels=None, ticks=None): #total month-by-month activity
    usg = np.sum(tl_arr, axis=0)
    plt.figure()
    plt.plot([i for i in range(len(usg))], usg)
#    if ticks:
#        plt.xticks(ticks, labels)
#    else:
#        plt.xticks(range(len(labels)), labels)
    plt.title("Total usage over time - " + name)
    plt.xlabel('Month', fontsize=16)
    plt.ylabel('Number of ' + name, fontsize=16)
    plt.show()

def indiv_usg(tl_arr, name): #total and consecutive month-by-month activity for each user
    total = dict()
    consecutive = dict()
    for user in tl_arr:
        tot_eng = 0
        cons_eng = []
        counter = 0
        for mth in user:
            if mth == 0:
                cons_eng.append(counter)
                counter = 0
            else:
                counter += 1
                tot_eng += 1
        tally(total, tot_eng)
        cons = 0
        if len(cons_eng) == 0:
            cons = tot_eng
        else:
            cons = max(cons_eng)
        tally(consecutive, cons)
    histo(total, 105, name + " - Total Months of Engagement", 'log')
    plt.ylabel("Number of users")
    plt.xlabel("Total months of engagement per user", fontsize=18)
    histo(consecutive, 50, name + " - Consecutive Months of Engagement", 'log')
    plt.ylabel("Number of users")
    plt.xlabel("Consecutive months of engagement per user", fontsize=18)
    
def compareTermRank(t1, t2):
    lst1 = []
    lst2 = []
    for k in t1:
        if k in t2:
            lst1.append(t1[k])
            lst2.append(t2[k])
        else:
            lst1.append(t1[k])
            lst2.append(0)
    for k in t2:
        if k not in t1:
            lst1.append(0)
            lst2.append(t2[k])
        else:
            continue
    js = jensenshannon(lst1, lst2)
    kl = entropy(lst1, lst2)
    print("Jensen-Shannon divergence: " + str(js))
    print("Kullback-Leibler divergence: " + str(kl))
            
