# IN PROGRESS


### Gov Sananga - Mapping and Analysis of Informal and Formal Enterprises 

Author: Roberto Moreira Diniz
Collaborators: Simone de Araújo Góes Assis, Moises Fabiano Júnior, Sérgio da Costa Côrtes, 
Institution: Centro Universitário IESB
Course: Data Science and Artificial Intelligence
City: Brasília, Brazil
Year: 2024-2025

Project Overview
Gov Sananga is a project aimed at mapping and analyzing informal businesses in communities using machine learning to interpret Google Street View images. The goal is to build a local economic activity database that can help create public policies to support business formalization and economic development.

1. Introduction
In Brazil, informal work has become widespread, especially in urban areas with lower income. Many businesses operate informally, lacking legal protection or support. The Gov Sananga project uses machine learning to analyze Google Street View images to identify businesses and economic activities in these areas.

The goal is to help map and understand local economic patterns and identify informal businesses. This data can be used to support policies that encourage business formalization and improve local economies.

2. Key Features
Machine Learning: Analyzes images from Google Street View to identify businesses and other economic activities.

Data Integration: Uses Amazon Web Services (AWS) for processing and storing data, ensuring scalability and security.

Dynamic Mapping: Allows the mapping of areas like Cidade Estrutural, with potential for adaptation to other cities.

Data Visualization: Provides an interactive interface using Streamlit to explore and analyze the results.

Security: Uses Amazon Cognito to manage user login and access securely.

3. Technology Stack
Google Street View API: Fetches images of urban areas.

AWS Lambda: Handles image processing and analysis.

Amazon Rekognition: Identifies objects and text within the images.

Amazon DynamoDB: Stores and organizes the analyzed data.

Streamlit: Provides a user-friendly interface for data exploration.

Amazon Cognito: Manages user authentication.

4. How It Works
Image Collection: Google Street View images are fetched for specific coordinates.

Image Analysis: AWS Lambda uses Amazon Rekognition to process these images, identifying key features like businesses, shops, and signs.

Data Storage: Results are stored in Amazon DynamoDB for easy access and analysis.

User Interface: A Streamlit app allows users to interact with the data, define analysis parameters, and visualize the results.

Security: User access is controlled using Amazon Cognito to ensure data privacy.

5. Future Improvements
Integration with NLP: Future updates will incorporate Natural Language Processing to analyze text in images for better business classification.

Expanded Data Sources: The platform can be enhanced with additional data sources to improve analysis accuracy.

6. Conclusion
Gov Sananga provides a foundation for mapping informal businesses in urban areas. It can be expanded with additional data sources and machine learning techniques to improve analysis and support public policies that encourage business formalization and economic growth.

7. License
This project is licensed under the MIT License - see the LICENSE file for details.


![media/gpt-img-repo.webp](https://raw.githubusercontent.com/s33ding/GovSananga/refs/heads/main/streamlit/app/media/gpt-img-repo.webp)

##### IN PROGRESS
