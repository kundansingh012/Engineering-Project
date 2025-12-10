# Board of Directors Network Analysis

## Overview
This project analyzes corporate board networks using director and company data to understand relationships, influence patterns, and board dynamics. The analysis includes centrality measures, demographic information, and temporal patterns in board memberships.

## Project Summary

We used **DEF 14A filings** (U.S. SEC data) to create a **network graph** of directors and companies.  
We then applied centrality metrics to score each director's **influence and connectedness**.

**Key Goals:**
- Find directors who are well-connected across companies
- Rank them by centrality (degree, eigenvector, betweenness)
- Suggest who might best help initiate a buyout
- Explore ethical concerns and responsible use

## Features
- Network analysis of director-company relationships
- Multiple centrality metrics (Eigenvector, Degree, Betweenness)
- Director tenure analysis
- Demographic insights
- Clustering analysis
- Interactive visualizations

## Data Sources
The project uses two main CSV files:
- `company_directorships.csv`: Contains board membership data including:
  - Director names
  - Company associations
  - Start/end dates
  - Software background indicators
- `director-details.csv`: Contains demographic information including:
  - Age
  - Compensation
  - Gender

## Key Features

### 1. Data Validation and Cleaning
- Duplicate removal
- Name standardization
- Missing value analysis
- Data type conversions

### 2. Network Analysis
- Bipartite network creation (directors-companies)
- Centrality measurements:
  - Eigenvector centrality (influence measure)
  - Degree centrality (direct connections)
  - Betweenness centrality (network bridge measure)

### 3. Temporal Analysis
- Director tenure calculations
- Board turnover patterns
- Historical trend analysis

### 4. Visualization Capabilities
- Network graphs
- Distribution plots
- Correlation heatmaps
- Interactive charts

## Key Functions

### `create_bipartite_network(df)`
Creates a bipartite network from director-company relationships.

### `most_common(series)`
Determines the most common value in a given pandas Series.

## Visualization Examples
The project includes various visualization capabilities:
- Top directors by different centrality measures
- Company connection networks
- Demographic distributions
- Correlation analysis
- Cluster visualizations

## Ethical Considerations
The project includes built-in ethical considerations:
- Data privacy awareness
- Bias detection in network analysis
- Responsible use of personal information
- Transparent methodology

## Future Enhancements
- Integration with Crunchbase Enterprise Dataset
- Enhanced visualization for non-technical audiences
- Additional demographic analysis capabilities
- Extended temporal pattern analysis
- 
✅ Tasks Completed
Task	Description
Task 1	Added betweenness centrality, explained all metrics
Task 2	Added influence summary, documented logic
Task 3	Used compensation as an additional ranking feature
Task 4	Proposed Crunchbase Enterprise Dataset ([https://www.crunchbase.com/discover/organization.companies](https://www.crunchbase.com/discover/organization.companies)) 
Task 5a	Created visual presentation with chart insights
Task 5c	Wrote ethics commentary about influence profiling risks

## Technologies Used

- Python 3.11+
- pandas, numpy
- scikit-learn
- matplotlib, seaborn
- Jupyter Notebook

