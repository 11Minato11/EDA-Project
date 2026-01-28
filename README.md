<<<<<<< HEAD
# Concert Tour Analysis - EDA

This project provides a comprehensive Exploratory Data Analysis (EDA) of global concert tours, focusing on data cleaning, feature engineering, and statistical validation of industry metrics.

## Key Features
- **Data Cleaning**: Sanitized "dirty" financial data (gross revenue, shows, rankings) using Regex and artist-specific median imputation.
- **Feature Engineering**: Derived efficiency metrics like *Gross per Show* and temporal features (*Tour Duration*, *Starting Era*).
- **Statistical Analysis**: Validated industry hypotheses using Pearson correlation (Volume vs. Revenue) and Welch’s T-Tests (Market era shifts).
- **Visualization**: Generated automated plots for revenue distributions, artist career stats, and performance benchmarks.

## Project Structure
- `data.py`: Core analysis and processing pipeline.
- `convert_to_pdf.py`: Report generation script.
- `Report_Concert_Tour_Analysis.pdf`: The final analytical report.
- `plots/`: Visual output from the EDA.

## Summary of Results
The analysis confirms a strong correlation (r=0.865) between show volume and total revenue, while highlighting that "Brand Premium" allows specific outliers to achieve higher efficiency. Automated cleaning was critical for accurate statistical testing.
=======
# EDA-Project
A Python-based EDA of global concert tours. It cleans "dirty" financial data using Regex, performs artist-specific median imputation, and engineers features like Gross per Show. Validates market trends via statistical testing (Pearson correlation, T-tests) and Seaborn visualizations. Outputs a professional PDF analysis report.
>>>>>>> 8554c74fbea5172e23f225203c92ed9d85cb0721
