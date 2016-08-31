#!/usr/bin/python
#encoding=utf-8
import os,sys
import os,shutil

def edit_distance(source, target):
    m = len(source) + 1
    n = len(target) + 1

    if m == 0:
        return n - 1
    if n == 0:
        return m - 1

    matrix = [[0 for i in range(0,m)]for j in range(0,n)]

    for i in range(0,m):
        matrix[0][i] = i
    for j in range(0,n):
        matrix[j][0] = j

    for j in range(1,n):
        for i in range(1,m):
            if source[i - 1] == target[j - 1]:
                matrix[j][i] = matrix[j - 1][i - 1]
            else:
                matrix[j][i] = min(matrix[j - 1][i - 1], matrix[j][i - 1], matrix[j - 1][i]) + 1

    return matrix[n - 1][m - 1]

def parse_file(src_file, is_ground_truth = True):
    file_dict = {}
    fp = open(src_file)
    lines = fp.readlines()
    for line in lines:
        line = line.translate(None, " ")
        line = line.translate(None, "\t")
        line = line.translate(None, "\n")
        line = line.translate(None, '\r')
        if is_ground_truth == True:
            word= line.split(".jpg")
        else:
            word = line.split(".jpg:")
        img_file = word[0]
        result = word[1].decode('utf-8')     
        #print img_file, result
        file_dict[img_file] = result
    fp.close()

    return file_dict

if __name__ == '__main__':

    text_path = '/data/Subtitle/Text_Result/'
    grount_truth_file = text_path + 'text_ground_truth.txt'
    ocr_file_baidu = text_path + 'result-baidu.txt'
    ocr_file_3c_add_border = text_path + 'result-add-border-3-channels.txt'
    ocr_file_3c = text_path + 'result-3-channels.txt'
    ocr_file_baidu1 = text_path + 'result-baidu.txt'

    check_img_path = '/data/Subtitle/Check_Img/'
    error_img_path = text_path + 'Error_Img/'

    text_check_error = text_path + 'text-check-error.txt'
    text_error = []
    
    if os.path.exists(text_check_error):
      os.remove(text_check_error)
    if os.path.exists(error_img_path):
      shutil.rmtree(error_img_path)
    os.mkdir(error_img_path)

    grount_truth_dict = parse_file(grount_truth_file)
    ocr_dict = parse_file(ocr_file_baidu, True)    # correct_num = 508, error_num = 1568

    total_num = 0
    correct_num = 0

    for key, value in ocr_dict.iteritems():
        total_num += 1
        if grount_truth_dict[key] != ocr_dict[key]:
            #print "Not equal, ", grount_truth_dict[key] , ocr_dict[key]
            shutil.copy(check_img_path + key + '.jpg', error_img_path + key + '.jpg')
            distance = edit_distance(grount_truth_dict[key], ocr_dict[key])
            text_error.append((key + '.jpg', distance, grount_truth_dict[key].encode('utf-8'), ocr_dict[key].encode('utf-8')))
        else:
            print "equal", grount_truth_dict[key], ocr_dict[key]
            correct_num += 1

    print "total_num = %d, correct_num = %d" %(total_num, correct_num)
    
    total_chars_num = 0
    error_num = 0
    for key, value in ocr_dict.iteritems():
        total_chars_num += len(grount_truth_dict[key])
        distance = edit_distance(grount_truth_dict[key], ocr_dict[key])
        error_num += distance
        #print distance #, grount_truth_dict[key], ocr_dict[key]

    print "total_chars_num = %d, error_num = %d" %(total_chars_num, error_num)
    
    text_error.sort(key=lambda x : x[0])
    with open(text_check_error,'wb') as tc:
        for line in text_error:
            context = '%s %s %s %s\n'%(line[0],line[1],line[2],line[3])
            tc.write(context)
