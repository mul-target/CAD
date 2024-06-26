import torch
from torch.utils.data import TensorDataset, DataLoader
from transformers import BertTokenizer, AutoTokenizer, BertweetTokenizer

# Tokenization
def convert_data_to_ids(tokenizer, target, target2, text):
    
    input_ids, seg_ids, attention_masks, sent_len = [], [], [], []
    for tar, sent in zip(target, text):
        encoded_dict = tokenizer.encode_plus(
                            tar,                            # Target to encode
                            sent,                           # Sentence to encode
                            add_special_tokens = True,      # Add '[CLS]' and '[SEP]'
                            max_length = 128,               # Pad & truncate all sentences.
                            padding = 'max_length',
                            return_attention_mask = True,   # Construct attn. masks.
                       )

        # Add the encoded sentence to the list.    
        input_ids.append(encoded_dict['input_ids'])
        seg_ids.append(encoded_dict['token_type_ids'])
        attention_masks.append(encoded_dict['attention_mask'])
        sent_len.append(sum(encoded_dict['attention_mask']))
    
    for tar, sent in zip(target2, text):
        encoded_dict = tokenizer.encode_plus(
                            tar,
                            sent,                      # Sentence to encode.
                            add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                            max_length = 128,           # Pad & truncate all sentences.
                            padding = 'max_length',
                            return_attention_mask = True,   # Construct attn. masks.
                       )

        # Add the encoded sentence to the list.    
        input_ids.append(encoded_dict['input_ids'])
    
    return input_ids, seg_ids, attention_masks, sent_len


# BERTweet tokenizer
def data_helper_bert(x_train_all,x_val_all,x_test_all,main_task_name,model_select):
    
    print('Loading data')
    
    x_train,y_train,x_train_target,y_train2,x_train_target2 = x_train_all[0],x_train_all[1],x_train_all[2],\
                                                              x_train_all[3],x_train_all[4]
    x_val,y_val,x_val_target,y_val2,x_val_target2 = x_val_all[0],x_val_all[1],x_val_all[2],x_val_all[3],x_val_all[4]
    x_test,y_test,x_test_target,y_test2,x_test_target2 = x_test_all[0],x_test_all[1],x_test_all[2],\
                                                         x_test_all[3],x_test_all[4]

    print("Length of original x_train: %d, the sum is: %d"%(len(x_train), sum(y_train)))
    print("Length of original x_val: %d, the sum is: %d"%(len(x_val), sum(y_val)))
    print("Length of original x_test: %d, the sum is: %d"%(len(x_test), sum(y_test)))
    
    # get the tokenizer

    tokenizer = BertweetTokenizer.from_pretrained("bertweet-base", normalization=True)

    # tokenization
    x_train_input_ids, x_train_seg_ids, x_train_atten_masks, x_train_len = \
                    convert_data_to_ids(tokenizer, x_train_target, x_train_target2, x_train)
    x_val_input_ids, x_val_seg_ids, x_val_atten_masks, x_val_len = \
                    convert_data_to_ids(tokenizer, x_val_target, x_val_target2, x_val)
    x_test_input_ids, x_test_seg_ids, x_test_atten_masks, x_test_len = \
                    convert_data_to_ids(tokenizer, x_test_target, x_test_target2, x_test)
    
    x_train_all = [x_train_input_ids,x_train_seg_ids,x_train_atten_masks,y_train,x_train_len,y_train2]
    x_val_all = [x_val_input_ids,x_val_seg_ids,x_val_atten_masks,y_val,x_val_len,y_val2]
    x_test_all = [x_test_input_ids,x_test_seg_ids,x_test_atten_masks,y_test,x_test_len,y_test2]
    
    return x_train_all,x_val_all,x_test_all


def data_load(x_all, batch_size, train_mode):

    y2 = [1 if y[half_y+i]==y[i] else 0 for i in range(len(y[:half_y]))] * 2

    half = int(len(x_all[0])/2)
    x_input_ids = torch.tensor(x_all[0][:half], dtype=torch.long).cuda()
    x_seg_ids = torch.tensor(x_all[1], dtype=torch.long).cuda()
    x_atten_masks = torch.tensor(x_all[2], dtype=torch.long).cuda()
    y = torch.tensor(x_all[3], dtype=torch.long).cuda()
    x_len = torch.tensor(x_all[4], dtype=torch.long).cuda()
    x_input_ids2 = torch.tensor(x_all[0][half:], dtype=torch.long).cuda()
    y2 = torch.tensor(y2, dtype=torch.long).cuda()

    tensor_loader = TensorDataset(x_input_ids,x_seg_ids,x_atten_masks,y,x_len,x_input_ids2,y2)
    data_loader = DataLoader(tensor_loader, shuffle=True, batch_size=batch_size)

    return x_input_ids, x_seg_ids, x_atten_masks, y, x_len, data_loader, x_input_ids2, y2
    

def sep_test_set(input_data):
    
    # split the combined test set for each target
    # trump_hillary数据集
    # trump_ted数据集
    return data_list