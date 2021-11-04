import tensorflow as tf
import cv2
import numpy as np
import os
from common import init_env, Unknown, finetune, TestEr, is_image
from tensorflow import keras
import shutil



args = init_env()
shutil.rmtree(args['test_result_dir'])
os.mkdir(args['test_result_dir'])
wrong_result_dir = os.path.join(args['test_result_dir'], 'wrong')
os.mkdir(wrong_result_dir)

tester = TestEr(args)

for threshold in args['threshold']:
    print('*' * 20 ,'阈值：', str(threshold), '*' * 20)
    right_num = 0
    unknown_num = 0
    total_num = np.finfo(np.float32).eps
    total_num_except_unknown = np.finfo(np.float32).eps
    all_classes_information = {}
    show_classes = args['classes'] + [Unknown]

    for root, dirs, files in os.walk(args['test_data_dir']):
        for item in dirs:
            os.makedirs(os.path.join(root, str(threshold), item).replace(args['test_data_dir'], args['test_result_dir']))
            if not os.path.exists(os.path.join(root, item).replace(args['test_data_dir'], wrong_result_dir)):
                os.mkdir(os.path.join(root, item).replace(args['test_data_dir'], wrong_result_dir))
        
        if len(files) > 0:
            root_dir, current_class = os.path.split(root)

            for item in args['classes']:
                os.makedirs(os.path.join(root_dir.replace(args['test_data_dir'], args['test_result_dir']), str(threshold), current_class, item))
            os.mkdir(os.path.join(root_dir.replace(args['test_data_dir'], args['test_result_dir']), str(threshold), current_class, Unknown))
            print('*'*20 + root + '*'*20)


            print('\t'.join(show_classes))
            classes_information = [0] * (len(show_classes))
            for item in files:
                if is_image(item):
                    image = cv2.imdecode(np.fromfile(os.path.join(root, item),np.uint8),flags=-1)

                    result = tester.infer(image)

                    image_class = finetune(result, args['classes'], threshold)
                    classes_information[show_classes.index(image_class)] += 1

                    if current_class in args['classes']:
                        total_num += 1
                        if image_class != Unknown:
                            total_num_except_unknown += 1
                        else:
                            unknown_num += 1
                        if current_class == image_class:
                            right_num += 1
        
                    if args['is_save_result']:
                        score_information = str(np.array(result*100, np.int32))
                        pre_label = result > 0.5
                        real_label = np.zeros(args['num_class'], dtype=np.bool)
                        real_label[args['classes'].index(current_class)] = 1
                        if np.sum(pre_label == real_label) != len(pre_label):
                            shutil.copy(os.path.join(root, item),os.path.join(wrong_result_dir, current_class, score_information + '##' + item))

                        shutil.copy(os.path.join(root, item),os.path.join(root_dir.replace(args['test_data_dir'], args['test_result_dir']), str(threshold), current_class, image_class, score_information + '##' + item))
                else:
                    print('Not image:{}'.format(os.path.join(root, item)))
                    os.remove(os.path.join(root, item))

            str_classes_information = [str(item) for item in classes_information]
            print('\t'.join(str_classes_information))
            all_classes_information[current_class] = classes_information

    print('*'*10, 'unknown:', unknown_num, '/', int(total_num), ' | ', unknown_num/total_num, '*'*10)
    print('*'*10, 'total_recall:', right_num, '/', int(total_num), ' | ', right_num/total_num, '*'*10)
    print('*'*10, 'total_except_unknown_recall:', right_num, '/', int(total_num_except_unknown), ' | ', right_num/total_num_except_unknown, '*'*10)

    precision_list = [0] * len(args['classes'])
    num_list = [[np.finfo(np.float32).eps] * len(show_classes)] * len(args['classes'])

    print('混淆矩阵：')
    table_header = show_classes + ['u_re','re']
    print('\t'+'\t'.join(table_header))
    for index, item in enumerate(args['classes']):
        classes_information = all_classes_information.get(item, None)
        if classes_information:
            except_unknown_recall = classes_information[show_classes.index(item)] / (sum(classes_information) - classes_information[-1])
            recall = classes_information[show_classes.index(item)] / sum(classes_information)
            classes_information = classes_information
            str_classes_information = [str(item) for item in classes_information] + ['{:.2f}'.format(except_unknown_recall * 100), '{:.2f}'.format(recall * 100)]
            print(item + '\t' + '\t'.join(str_classes_information))

            precision_list[index] = classes_information[show_classes.index(item)]
            num_list[index] = classes_information


    precision_numpy = np.array(precision_list, dtype=np.float32)
    num_numpy = np.sum(np.array(num_list, dtype=np.float32)[:,:-1], axis=0)
    precision_list = (precision_numpy / num_numpy).tolist()
    str_precision_information = ['{:.2f}'.format(item * 100) for item in precision_list]
    print('pr' + '\t' + '\t'.join(str_precision_information))

