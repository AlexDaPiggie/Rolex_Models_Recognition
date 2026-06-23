import torch
from src.training.evaluate import top_prediction 

def test_top_prediction(): 
    class_names = ['datejust', 'gmt_master', 'submariner']
    logits = torch.tensor([[0.0, 1.0, 3.0]])
    result = top_prediction(logits, class_names)
    assert result ['predicted_class'] == 'submariner'
    assert result['confidence'] > 0.8
    assert set (result['probabilities']) == set(class_names)