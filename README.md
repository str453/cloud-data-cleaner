# cloud-data-cleaner
A privacy-focused cloud tool for encrypting, masking, and securely storing CSV files using customizable algorithms. 

## Project Goal

Cloud Data Cleaner provides a simple, secure, cloud-based solution for encrypting and decrypting CSV files. Users can choose from various algorithms to protect their data.

## Features

- Encrypt/decrypt CSV files with user-selected algorithms
- Store and access files securely via Google Cloud Platform
- Web-based UI for uploads and management
- Authentication via Firebase/Auth0
- Persistent storage with MySQL
- Customizable data masking

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Java (Spring Boot, Thymeleaf)
- **Cloud & Storage:** Google Cloud Platform (GCP)
- **Authentication:** Firebase/Auth0
- **Database:** MySQL
- **DevOps:** GitHub

## Getting Started

> This project is under active development and may change rapidly.

### Prerequisites

- Java 11+
- Maven
- Node.js & npm (for frontend)
- GCP account/credentials
- MySQL
- Firebase project

### Installation

1. **Clone the repository**
    ```sh
    git clone https://github.com/b-jr/cloud-data-cleaner.git
    cd cloud-data-cleaner
    ```

2. **Backend Setup**
    - Configure GCP and MySQL credentials in `application.properties`.
    - Run:
      ```sh
      mvn spring-boot:run
      ```

3. **Frontend Setup**
    - Coming soon.

### Usage

- Access the UI at `http://localhost:8080`
- Upload your CSV file
- Select encryption/decryption options
- Authenticate via Firebase/Auth0
- Download or access files via GCP

## Integration Steps (To be updated)

Details about connecting to GCP, environment variables, and integration testing will be added here.

## Contributors

To be added.

## License

This project is licensed under the MIT License.