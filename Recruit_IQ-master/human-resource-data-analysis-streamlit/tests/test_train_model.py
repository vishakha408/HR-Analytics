"""Unit tests for train_attrition_model function"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ml_models import train_attrition_model, load_trained_model, predict_attrition


@pytest.fixture
def sample_hr_data():
    """Create sample HR dataset"""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'Age': np.random.randint(20, 60, n_samples),
        'MonthlyIncome': np.random.randint(2000, 10000, n_samples),
        'YearsAtCompany': np.random.randint(0, 30, n_samples),
        'DistanceFromHome': np.random.randint(1, 30, n_samples),
        'JobSatisfaction': np.random.randint(1, 5, n_samples),
        'EnvironmentSatisfaction': np.random.randint(1, 5, n_samples),
        'JobInvolvement': np.random.randint(1, 4, n_samples),
        'JobLevel': np.random.randint(1, 5, n_samples),
        'NumCompaniesWorked': np.random.randint(0, 10, n_samples),
        'TotalWorkingYears': np.random.randint(0, 40, n_samples),
        'YearsInCurrentRole': np.random.randint(0, 20, n_samples),
        'YearsSinceLastPromotion': np.random.randint(0, 15, n_samples),
        'PercentSalaryHike': np.random.randint(11, 26, n_samples),
        'TrainingTimesLastYear': np.random.randint(0, 6, n_samples),
        'Attrition': np.random.choice(['Yes', 'No'], n_samples, p=[0.2, 0.8])
    }
    
    return pd.DataFrame(data)


def test_train_attrition_model_basic(sample_hr_data):
    """Test basic training functionality"""
    result = train_attrition_model(sample_hr_data)
    
    assert isinstance(result, dict)
    assert 'model' in result
    assert 'accuracy' in result
    assert 'roc_auc' in result
    assert 'model_path' in result
    
    # Check accuracy is in valid range
    assert 0 <= result['accuracy'] <= 1
    assert 0 <= result['roc_auc'] <= 1


def test_train_attrition_model_with_custom_features(sample_hr_data):
    """Test training with custom features"""
    features = ['Age', 'MonthlyIncome', 'YearsAtCompany']
    result = train_attrition_model(sample_hr_data, features=features)
    
    assert result['feature_names'] == features
    assert len(result['feature_importance']) == len(features)


def test_train_attrition_model_invalid_feature(sample_hr_data):
    """Test error handling for invalid features"""
    features = ['NonExistentFeature']
    
    with pytest.raises(ValueError):
        train_attrition_model(sample_hr_data, features=features)


def test_train_attrition_model_invalid_target(sample_hr_data):
    """Test error handling for invalid target"""
    with pytest.raises(ValueError):
        train_attrition_model(sample_hr_data, target='NonExistentTarget')


def test_train_attrition_model_metrics(sample_hr_data):
    """Test that all metrics are returned"""
    result = train_attrition_model(sample_hr_data)
    
    required_metrics = ['accuracy', 'roc_auc', 'precision', 'recall', 'f1']
    for metric in required_metrics:
        assert metric in result
        assert isinstance(result[metric], (float, np.floating))
        assert 0 <= result[metric] <= 1


def test_train_attrition_model_sizes(sample_hr_data):
    """Test train/test split sizes"""
    test_size = 0.25
    result = train_attrition_model(sample_hr_data, test_size=test_size)
    
    total_size = result['train_size'] + result['test_size']
    assert total_size == len(sample_hr_data)
    assert result['test_size'] / total_size == pytest.approx(test_size, rel=0.1)


def test_model_saved_to_disk(sample_hr_data):
    """Test that model is saved to disk"""
    result = train_attrition_model(sample_hr_data)
    
    assert os.path.exists(result['model_path'])
    assert result['model_path'].endswith('.pkl')


def test_load_trained_model(sample_hr_data):
    """Test loading saved model"""
    result = train_attrition_model(sample_hr_data)
    
    loaded_model = load_trained_model(result['model_path'])
    assert loaded_model is not None
    assert hasattr(loaded_model, 'predict')
    assert hasattr(loaded_model, 'predict_proba')


def test_predict_attrition_binary(sample_hr_data):
    """Test binary predictions"""
    result = train_attrition_model(sample_hr_data)
    
    predictions = predict_attrition(
        result['model'], 
        sample_hr_data, 
        features=result['feature_names'],
        return_proba=False
    )
    
    assert len(predictions) == len(sample_hr_data)
    assert set(predictions).issubset({0, 1})


def test_predict_attrition_proba(sample_hr_data):
    """Test probability predictions"""
    result = train_attrition_model(sample_hr_data)
    
    proba = predict_attrition(
        result['model'], 
        sample_hr_data, 
        features=result['feature_names'],
        return_proba=True
    )
    
    assert len(proba) == len(sample_hr_data)
    assert np.all(proba >= 0)
    assert np.all(proba <= 1)


def test_feature_importance_calculation(sample_hr_data):
    """Test feature importance scores"""
    result = train_attrition_model(sample_hr_data)
    
    importance = result['feature_importance']
    assert isinstance(importance, dict)
    assert len(importance) == len(result['feature_names'])
    
    # All importance scores should be non-negative
    assert all(score >= 0 for score in importance.values())
    # Total importance should be around 1
    assert sum(importance.values()) > 0


def test_automatic_feature_selection(sample_hr_data):
    """Test automatic numeric feature selection"""
    result = train_attrition_model(sample_hr_data)
    
    # Should select numeric columns except target
    expected_numeric = sample_hr_data.select_dtypes(include=[np.number]).columns.tolist()
    expected_numeric = [col for col in expected_numeric if col != 'Attrition']
    
    assert set(result['feature_names']).issubset(set(expected_numeric))


def test_different_test_sizes(sample_hr_data):
    """Test different test_size parameters"""
    for test_size in [0.1, 0.2, 0.3, 0.4]:
        result = train_attrition_model(sample_hr_data, test_size=test_size)
        
        total = result['train_size'] + result['test_size']
        actual_test_pct = result['test_size'] / total
        
        # Allow 10% relative tolerance
        assert abs(actual_test_pct - test_size) < 0.1


def test_metadata_saved(sample_hr_data):
    """Test that metadata is saved"""
    result = train_attrition_model(sample_hr_data)
    
    assert os.path.exists(result['metadata_path'])
    
    # Load and verify metadata
    import json
    with open(result['metadata_path'], 'r') as f:
        metadata = json.load(f)
    
    assert 'features' in metadata
    assert 'target' in metadata
    assert 'timestamp' in metadata
    assert metadata['target'] == 'Attrition'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
