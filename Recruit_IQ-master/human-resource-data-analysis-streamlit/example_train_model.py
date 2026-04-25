"""Example script demonstrating train_attrition_model function"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from ml_models import train_attrition_model, load_trained_model, predict_attrition

# Example 1: Load sample HR data and train model
if __name__ == "__main__":
    print("=" * 70)
    print("Attrition Model Training Example")
    print("=" * 70)
    
    # Load data
    try:
        df = pd.read_csv('input_data/raw_hr_data.csv')
        print(f"\n✓ Loaded data with {len(df)} records and {len(df.columns)} columns")
    except FileNotFoundError:
        print("\n✗ Error: Could not find 'input_data/raw_hr_data.csv'")
        sys.exit(1)
    
    print(f"  Columns: {list(df.columns[:5])}...")
    print(f"  Target column 'Attrition': {df['Attrition'].value_counts().to_dict()}")
    
    # Example 1: Train with default numeric features
    print("\n" + "-" * 70)
    print("Example 1: Train with automatic numeric feature selection")
    print("-" * 70)
    
    try:
        result = train_attrition_model(df, target='Attrition', test_size=0.2)
        
        print(f"\n✓ Model trained successfully!")
        print(f"  - Accuracy: {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
        print(f"  - ROC-AUC: {result['roc_auc']:.4f}")
        print(f"  - Precision: {result['precision']:.4f}")
        print(f"  - Recall: {result['recall']:.4f}")
        print(f"  - F1-Score: {result['f1']:.4f}")
        print(f"  - Model saved to: {result['model_path']}")
        print(f"  - Features used: {len(result['feature_names'])} columns")
        print(f"  - Training set size: {result['train_size']}")
        print(f"  - Test set size: {result['test_size']}")
        
        # Show top 5 important features
        print(f"\n  Top 5 Important Features:")
        sorted_features = sorted(result['feature_importance'].items(), 
                                key=lambda x: x[1], reverse=True)[:5]
        for i, (feature, importance) in enumerate(sorted_features, 1):
            print(f"    {i}. {feature}: {importance:.4f}")
    
    except Exception as e:
        print(f"\n✗ Error during training: {str(e)}")
        sys.exit(1)
    
    # Example 2: Train with specific features
    print("\n" + "-" * 70)
    print("Example 2: Train with manually selected features")
    print("-" * 70)
    
    selected_features = ['Age', 'MonthlyIncome', 'YearsAtCompany', 
                        'DistanceFromHome', 'JobSatisfaction', 'OverTime']
    
    # Check if all features exist
    available_features = [f for f in selected_features if f in df.columns]
    missing_features = [f for f in selected_features if f not in df.columns]
    
    if missing_features:
        print(f"\n  Note: Some features not available: {missing_features}")
        print(f"  Using available features: {available_features}")
        selected_features = available_features
    
    try:
        result2 = train_attrition_model(df, target='Attrition', 
                                       features=selected_features, test_size=0.2)
        
        print(f"\n✓ Model trained with selected features!")
        print(f"  - Accuracy: {result2['accuracy']:.4f} ({result2['accuracy']*100:.2f}%)")
        print(f"  - ROC-AUC: {result2['roc_auc']:.4f}")
        print(f"  - Features used: {result2['feature_names']}")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    # Example 3: Load model and make predictions
    print("\n" + "-" * 70)
    print("Example 3: Load model and make predictions")
    print("-" * 70)
    
    try:
        loaded_model = load_trained_model('model/attrition_model.pkl')
        print(f"\n✓ Model loaded successfully!")
        
        # Make predictions on first 10 records
        predictions = predict_attrition(loaded_model, df.iloc[:10], 
                                       features=result['feature_names'])
        proba = predict_attrition(loaded_model, df.iloc[:10], 
                                 features=result['feature_names'], return_proba=True)
        
        print(f"\n  First 10 Predictions:")
        print(f"  Index | Binary Pred | Probability")
        print(f"  ------|-------------|------------")
        for i in range(10):
            pred_label = "At Risk" if predictions[i] == 1 else "Stable"
            print(f"  {i:5d} | {pred_label:11s} | {proba[i]:10.2%}")
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("Example completed!")
    print("=" * 70)
