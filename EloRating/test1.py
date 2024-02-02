import encodings
import chardet

with open('2023_LoL_esports_match_data_from_OraclesElixir.csv', 'rb') as f:
    result = chardet.detect(f.read())
    file_encoding = result['encoding']
    print(result)