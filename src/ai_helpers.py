# src/ai_helpers.py

"""
This file contains helper functions for various AI-related tasks.
It provides reusable components for common operations like
data preprocessing, model evaluation, and logging.

Author: Bard
Date: 2023-10-27
"""

import logging
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define a logger for this module
logger = logging.getLogger(__name__)

def preprocess_data(data):
    """
    Preprocesses the input data.

    Args:
        data (list or numpy.ndarray): The input data to be processed.

    Returns:
        numpy.ndarray: The processed data.

    Raises:
        TypeError: If the input data is not a list or numpy.ndarray.
    """
    try:
        if not isinstance(data, (list, np.ndarray)):
            raise TypeError("Input data must be a list or numpy.ndarray.")
        
        # Example preprocessing: Convert to numpy array and scale to [0, 1]
        data = np.array(data)
        data = (data - np.min(data)) / (np.max(data) - np.min(data))
        logger.info("Data preprocessed successfully.")
        return data
    except Exception as e:
        logger.error(f"Error during data preprocessing: {e}")
        return None

def evaluate_model(predictions, actual_values):
    """
    Evaluates the model's performance.

    Args:
        predictions (numpy.ndarray): The model's predictions.
        actual_values (numpy.ndarray): The actual values.

    Returns:
        float: The evaluation metric (e.g., mean squared error).
    """
    try:
        # Example: Mean Squared Error
        mse = np.mean((predictions - actual_values)**2)
        logger.info(f"Mean Squared Error: {mse}")
        return mse
    except Exception as e:
        logger.error(f"Error during model evaluation: {e}")
        return None

def log_event(message, level='info'):
    """
    Logs a message with the specified level.

    Args:
        message (str): The message to log.
        level (str): The logging level (e.g., 'info', 'warning', 'error').
    """
    try:
        logger.log(level, message)
    except Exception as e:
        logger.error(f"Error during logging: {e}")

if __name__ == '__main__':
    # Example Usage
    example_data = [1, 2, 3, 4, 5]
    processed_data = preprocess_data(example_data)
    if processed_data is not None:
        print("Processed Data:", processed_data)

        predictions = np.array([2.5, 3.0, 3.5, 4.0, 4.5])
        mse = evaluate_model(predictions, example_data)
        if mse is not None:
            print("Mean Squared Error:", mse)

        log_event("Example completed successfully.")