


category_dict = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'}, 'Trailers':{'img':'trailer.webp'}}

category_dict_all = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Compaction':{'img':'compaction.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'},
    'Mowers':{'img':'mower.webp'}, 'Trailers':{'img':'trailer.webp'}, 'UTV':{'img':'utv.webp'}}

cat_list = list(category_dict.keys())

equipment_dict = {'2024_Bobcat_E26': {
        'brand': 'Bobcat',
        'model': 'E-26',
        'yr': '2024',
        'img': 'bobcat-e26.webp',
        'sn': '2024E26',
        'wt': '7500',
        'ppd': 225,
        'ppw': 875,
        'dfee': 200,
        'ifee': 25,
        'category': 'Compact Earth Moving',
        'note':'7500 Lb Mini Excavator',
        'note2':'61" Wide, Long Arm, Zero-Tailswing',
        'avl': True
    },'2024_Bobcat_T595': {
            'brand': 'Bobcat',
            'model': 'T595',
            'yr': '2024',
            'img': 'bobcat-t595.webp',
            'sn': '2024T595',
            'wt': '8000',
            'ppd': 375,
            'ppw': 1350,
            'dfee': 200,
            'ifee': 25,
            'category': 'Compact Earth Moving',
            'note':'8000 Lb Track Loader',
            'note2':'68" Wide, Two-speed',
            'avl': True
    },'POWERMATE_3500': {
            'brand': 'Coleman',
            'model': 'Powermate Vantage 3500',
            'yr': '',
            'img': 'powermate5.jpg',
            'sn': 'POWERMATE35001',
            'wt': '60',
            'ppd': 50,
            'ppw': 200,
            'dfee': 50,
            'ifee': 0,
            'category': 'Generators',
            'note':'3500 Watt Generator',
            'note2':'Briggs & Stratton Engine',
            'avl': True
    },'NorthStar_8000': {
            'brand': 'Northstar',
            'model': '8kW Generator',
            'yr': '',
            'img': 'northstar8kw.webp',
            'sn': 'NORTHSTAR8KW001',
            'wt': '200',
            'ppd': 100,
            'ppw': 400,
            'dfee': 50,
            'ifee': 0,
            'category': 'Generators',
            'note':'8000 Watt Generator',
            'note2':'Wheel Kit, Honda 390cc Engine',
            'avl': True
    },'BAUER_DEMO_HAMMER': {
            'brand': 'BAUER',
            'model': 'Demolition Hammer',
            'yr': '',
            'img': 'demohammer.jpg',
            'sn': 'DEMOHAMMER1',
            'wt': '20',
            'ppd': 50,
            'ppw': 175,
            'dfee': 50,
            'ifee': 0,
            'category': 'Hand and Power Tools',
            'note':'Demolition Hammer',
            'note2':'12.5 Amp, Corded, SDS Max Type',
            'avl': True
    },'STIHL_025_SAW': {
            'brand': 'STIHL',
            'model': '025 Chainsaw',
            'yr': '',
            'img': 'stihl-ms-250.jpg',
            'sn': 'STIHL_025',
            'wt': '10',
            'ppd': 50,
            'ppw': 175,
            'dfee': 50,
            'ifee': 0,
            'category': 'Hand and Power Tools',
            'note':'16" Professional Chainsaw',
            'note2':'44cc, 16in Bar',
            'avl': True
    },'ECHO_CS450_SAW': {
            'brand': 'ECHO',
            'model': 'CS-450 Chainsaw',
            'yr': '',
            'img': 'Echo_CS-450.jpg',
            'sn': 'ECHO_CS450',
            'wt': '11',
            'ppd': 55,
            'ppw': 200,
            'dfee': 50,
            'ifee': 0,
            'category': 'Hand and Power Tools',
            'note':'20" Professional Chainsaw',
            'note2':'45cc, 20in Bar',
            'avl': True
    }}

eq_d = equipment_dict

att_list = {'2024_Bobcat_E26':['16" Toothed Bucket','Hydraulic Thumb'],
            '2024_Bobcat_E42':['24" Toothed Bucket','Hydraulic Thumb'],
            '2024_Bobcat_T595':['68" Heavy Duty Bucket']}
