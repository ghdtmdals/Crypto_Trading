import numpy as np
import pandas as pd

### Get Initial Confusion Matrix and R_0 from Dataframe at T=0
### Get R_t+1 from Dataframe at T=1
### Update Confusion Matrix using R_0 and R_t+1
### Update R_0

def _get_r0(df, labels):
    r0 = np.array([[[0, 0], [0, 0]]])
    for i in range(len(labels) - 1):
        r0 = np.concat((r0, np.array([[[0, 0], [0, 0]]])), axis = 0)

    ### First Record in Dataframe (R_0)
    pred = df.loc[0, 'trade_call']
    target = df.loc[0, 'target']
    for j, label in enumerate(labels):
        pred_pos = 1 if pred == label else 0
        actual_pos = 1 if target == label else 0
        r0[j, pred_pos, actual_pos] += 1
    
    return r0

def create_confusion_matrix(df, labels):
    ### Initialize an Empty Confusion Matrix per Class
    r0 = _get_r0(df, labels)
    
    ### Confusion Matrix
    arr = r0.copy()
    for i in range(1, len(df)):
        pred = df.loc[i, 'trade_call']
        target = df.loc[i, 'target']

        for j, label in enumerate(labels):
            pred_pos = 1 if pred == label else 0
            actual_pos = 1 if target == label else 0
            arr[j, pred_pos, actual_pos] += 1
    
    return arr, r0, df.loc[1:].reset_index(drop = True)

def update_confusion_matrix(t1, r0, cm_t, df, labels):
    rt1 = np.array([[[0, 0], [0, 0]]])
    for i in range(len(labels) - 1):
        rt1 = np.concat((rt1, np.array([[[0, 0], [0, 0]]])), axis = 0)

    ## Last Record in New Dataframe (R_t+1)
    for j, label in enumerate(labels):
        pred_pos = 1 if t1['trade_call'] == label else 0
        actual_pos = 1 if t1['target'] == label else 0
        rt1[j, pred_pos, actual_pos] += 1
    
    cm_t1 = cm_t - r0 + rt1
    r0 = _get_r0(df, labels)

    df = pd.concat([df, t1.to_frame().T], axis = 0)
    df = df.loc[1:].reset_index(drop = True)

    return cm_t1, r0, df

def custom_precison_recall_fscore(confusion_matrix, labels, average = 'weighted', n_digits = 3):
    #############       Neg   TN: [0, 0]   FN: [0, 1]
    ############# Pred
    #############       Pos   FP: [1, 0]   TP: [1, 1]
    #############                 Neg         Pos
    #############                      Actual
    
    avg_precision, avg_recall, avg_f1 = 0, 0, 0

    if average == "weighted":
        supports = []
        precisions = []
        recalls = []
        f1_scores = []
        for i in range(len(labels)):
            ### True Positive + False Negative
            supports.append(confusion_matrix[i][0, 1] + confusion_matrix[i][1, 1])
            ### TP / (TP + FP)
            precision = confusion_matrix[i][1, 1] / (confusion_matrix[i][1, 1] + confusion_matrix[i][1, 0])
            
            ### TP / (TP + FN)
            recall = confusion_matrix[i][1, 1] / (confusion_matrix[i][1, 1] + confusion_matrix[i][0, 1])

            f1 = 2 * ((recall * precision) / (recall + precision))

            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)
        
        weights = []
        for support in supports:
            weights.append(support / sum(supports))
    
        for i in range(len(labels)):
            avg_precision += precisions[i] * weights[i]
            avg_recall += recalls[i] * weights[i]
            avg_f1 += f1_scores[i] * weights[i]
        
    return round(float(avg_precision), n_digits), round(float(avg_recall), n_digits), round(float(avg_f1), n_digits)