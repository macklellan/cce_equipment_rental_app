


category_dict = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'}, 'Trailers':{'img':'trailer.webp'}}

category_dict_all = {'Compact Earth Moving':{'img':'bobcat-e42.webp'}, 'Compaction':{'img':'compaction.webp'}, 'Generators':{'img':'generator.webp'}, 'Hand and Power Tools':{'img':'demohammer.jpg'},
    'Mowers':{'img':'mower.webp'}, 'Trailers':{'img':'trailer.webp'}, 'UTV':{'img':'utv.webp'}}

cat_list = list(category_dict.keys())

equipment_dict = {'2024_Bobcat_E26': {
        'brand': 'Bobcat',
        'model': 'E-26',
        'yr': '2024',
        'img': 'E26.jpg',
        'sn': '2024E26',
        'wt': '7500',
        'ppd': 225,
        'ppw': 875,
        'dfee': 200,
        'ifee': 25,
        'category': 'Compact Earth Moving',
        'note':'7500 Lb Mini Excavator',
        'note2':'Long Arm, X-change',
        'avl': True
    },'2024_Bobcat_T595': {
            'brand': 'Bobcat',
            'model': 'T595',
            'yr': '2024',
            'img': 'bobcat-t595.webp',
            'sn': '2024T595',
            'wt': '8000',
            'ppd': 400,
            'ppw': 1500,
            'dfee': 200,
            'ifee': 25,
            'category': 'Compact Earth Moving',
            'note':'8000 Lb Track Loader',
            'note2':'Two-speed',
            'avl': True
    }}

eq_d = equipment_dict

att_list = {'2024_Bobcat_E26':['16" Toothed Bucket','Hydraulic Thumb (Equipped Standard)'],
            '2024_Bobcat_E42':['24" Toothed Bucket','Hydraulic Thumb (Equipped Standard)'],
            '2024_Bobcat_T595':['68" Heavy Duty Bucket']}
