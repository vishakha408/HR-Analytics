"""Tests for ML model training and prediction"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml_models import AttritionPredictor


@pytest.fixture
def sample_data():
    """Create sample HR data for testing"""
    data = {
        'Age': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70],
        'MonthlyIncome': [2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000],
        'YearsAtCompany': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Department': ['Sales', 'HR', 'IT', 'Sales', 'HR', 'IT', 'Sales', 'HR', 'IT', 'Sales'],
        'JobRole': ['Manager', 'Analyst', 'Developer', 'Manager', 'Analyst', 
                   'Developer', 'Manager', 'Analyst', 'Developer', 'Manager'],
        'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'Attrition': ['No', 'Yes', 'No', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'No'],
        'JobSatisfaction': ['Satisfied', 'Dissatisfied', 'Neutral', 'Satisfied', 'Very Dissatisfied',
                           'Satisfied', 'Satisfied', 'Dissatisfied', 'Neutral', 'Satisfied'],
        'DistanceFromHome': [5, 10, 15, 20, 25, 10, 5, 15, 20, 10],
        'YearsInCurrentRole': [1, 2, 1, 3, 2, 4, 1, 2, 3, 1],
        'YearsSinceLastPromotion': [0, 1, 2, 1, 0, 2, 1, 2, 1, 0],
        'PercentSalaryHike': [11, 12, 13, 14, 15, 11, 12, 13, 14, 15],
        'TrainingTimesLastYear': [2, 3, 2, 1, 2, 3, 2, 1, 2, 3],
        'OverTime': ['No', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes'],
        'EnvironmentSatisfaction': [3, 2, 4, 3, 1, 4, 3, 2, 4, 3],
        'JobInvolvement': [3, 2, 4, 3, 2, 4, 3, 2, 4, 3],
        'JobLevel': [1, 2, 3, 2, 1, 3, 2, 1, 3, 2],
        'NumCompaniesWorked': [2, 1, 3, 2, 1, 0, 2, 1, 3, 2],
        'TotalWorkingYears': [5, 8, 10, 12, 15, 18, 20, 22, 25, 30],
        'HourlyRate': [65, 70, 75, 80, 85, 90, 95, 100, 105, 110],
        'DailyRate': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900],
        'MonthlyRate': [5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500],
        'RelationshipSatisfaction': [3, 2, 4, 3, 2, 4, 3, 2, 4, 3],
        'StockOptionLevel': [0, 1, 2, 1, 0, 2, 1, 0, 2, 1],
        'WorkLifeBalance': [3, 2, 4, 3, 2, 4, 3, 2, 4, 3],
        'MaritalStatus': ['Single', 'Married', 'Divorced', 'Single', 'Married', 
                         'Divorced', 'Single', 'Married', 'Divorced', 'Single'],
        'BusinessTravel': ['Travel_Rarely', 'Travel_Frequently', 'Non-Travel', 'Travel_Rarely',
                          'Travel_Frequently', 'Non-Travel', 'Travel_Rarely', 'Travel_Frequently',
                          'Non-Travel', 'Travel_Rarely'],
        'Education': [1, 2, 3, 2, 1, 3, 2, 1, 3, 2],
        'EducationField': ['Life Sciences', 'Medical', 'Other', 'Life Sciences', 'Medical',
                          'Other', 'Life Sciences', 'Medical', 'Other', 'Life Sciences'],
    }
    
    return pd.DataFrame(data)


def test_model_initialization():
    """Test that model initializes correctly"""
    model = AttritionPredictor()
    assert model.is_trained == False
    assert model.feature_columns is None
    assert len(model.metrics) == 0


def test_train_predict_shape(sample_data):
    """Test that model.fit returns correct shapes for predict_proba"""
    model = AttritionPredictor()
    metrics = model.train(sample_data, test_size=0.2)
    
    assert model.is_trained == True
    assert metrics is not None
    assert 'test_accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'roc_auc' in metrics
    
    # Test prediction shape
    pred_proba = model.predict_proba(sample_data)
    assert pred_proba.shape == (len(sample_data), 2)
    assert pred_proba.min() >= 0
    assert pred_proba.max() <= 1


def test_predict_output_columns(sample_data):
    """Test that predictions add expected columns"""
    model = AttritionPredictor()
    model.train(sample_data, test_size=0.2)
    
    # Test predictions
    pred_proba = model.predict_proba(sample_data)
    pred_labels = model.predict(sample_data)
    
    # Check shapes
    assert pred_proba.shape[0] == len(sample_data)
    assert pred_labels.shape[0] == len(sample_data)
    
    # Check values are binary for labels
    assert set(pred_labels).issubset({0, 1})


def test_feature_importance(sample_data):
    """Test that feature importance is calculated"""
    model = AttritionPredictor()
    model.train(sample_data, test_size=0.2)
    
    feature_importance = model.get_feature_importance(top_n=5)
    
    assert isinstance(feature_importance, dict)
    assert len(feature_importance) <= 5
    assert all(isinstance(k, str) for k in feature_importance.keys())
    assert all(isinstance(v, (int, float)) for v in feature_importance.values())


def test_model_metrics_values(sample_data):
    """Test that model metrics are in valid ranges"""
    model = AttritionPredictor()
    metrics = model.train(sample_data, test_size=0.2)
    
    # All metrics should be between 0 and 1
    assert 0 <= metrics['test_accuracy'] <= 1
    assert 0 <= metrics['precision'] <= 1
    assert 0 <= metrics['recall'] <= 1
    assert 0 <= metrics['f1'] <= 1
    assert 0 <= metrics['roc_auc'] <= 1


def test_model_save_load(sample_data, tmp_path):
    """Test model save and load functionality"""
    model = AttritionPredictor()
    model.train(sample_data, test_size=0.2)
    
    # Save model
    model_path = tmp_path / "test_model.pkl"
    model.save(str(model_path))
    
    assert model_path.exists()
    
    # Load model
    loaded_model = AttritionPredictor.load(str(model_path))
    
    assert loaded_model.is_trained == True
    assert loaded_model.feature_columns == model.feature_columns
    assert loaded_model.get_metrics()['test_accuracy'] == model.get_metrics()['test_accuracy']


def test_preprocessing_consistency(sample_data):
    """Test that preprocessing is consistent"""
    model = AttritionPredictor()
    model.train(sample_data, test_size=0.2)
    
    # Preprocess same data twice
    processed1 = model._preprocess_data(sample_data, fit_encoders=False)
    processed2 = model._preprocess_data(sample_data, fit_encoders=False)
    
    # Should be identical
    pd.testing.assert_frame_equal(processed1, processed2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
