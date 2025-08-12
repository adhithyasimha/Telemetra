# Telemetra - Real-Time Formula 1 Data Pipeline

This project builds a robust real-time data pipeline for Formula 1 racing data. It ingests live data from the **livef1** library, processes it using streaming technologies, and stores the processed data in **Amazon Redshift** for further use.

The pipeline leverages **Kafka from Confluent Cloud** as the central message queue to enable decoupled data streaming. To ensure fault tolerance and high availability, a **load balancer** is incorporated into the architecture. Kafka and system configurations are managed via property files for easy maintenance and flexibility.

## Key Features

- **Real-Time Data Ingestion**: Captures live Formula 1 data from the `livef1` library.  
- **Kafka Integration**: Uses Kafka hosted on Confluent Cloud as the central message queue for streaming and component decoupling.  
- **Data Transformation**: Processes and cleans data using Spark Streaming for efficient handling.  
- **Data Storage**: Stores processed data exclusively in Amazon Redshift for reliable, analytics-ready storage.  
- **Fault Tolerance**: Implements a load balancer to ensure high availability and fault tolerance across services.  
- **Configuration Driven**: Loads Kafka and system configurations from property files for flexible and maintainable setup.



## Architecture
<img width="1039" height="598" alt="Screenshot 2025-08-11 at 10 26 26 PM" src="https://github.com/user-attachments/assets/5abf8054-c35b-4b12-9694-34e99c03d2a9" />

