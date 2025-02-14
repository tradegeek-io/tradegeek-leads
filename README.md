# BubbleZohoConnector-Minor Service Handling

This repository contains the source code for a microservice designed to integrate with a [Bubble](https://bubble.io/) application and interact with Zoho CRM. The microservice provides functionalities to handle vehicle Submission, Activation and Lead Generation.


## Overview

This microservice enhances the functionality of a Bubble app by providing backend services that handle complex operations outside the scope of Bubble's native capabilities.

## Setup and Installation

### Prerequisites
  An azure function(python 3.11 and runtime ~4)

### Steps

1. **Clone the Repository:**
   - Clone the repository using the following command:
     ```bash
     git clone https://github.com/rahul-08-11/BubbleCRMConnectorv1.0.git
     ```

2. **Configure `workflow`:**
   - run the below command to update workflow by replace `app-name` with new function name:
     ```bash
     nano .github/workflows/azure-functions-app-python.yml 
     ```
   - Update the configuration file with your Azure Function name.

3. **Create a Git Repository (if not already created):**
   - Create a new repository on GitHub or your preferred Git hosting service.
   - Copy the repository URL.

4. **Reinitialize Git Repository:**
   - Navigate back to the root of your project directory:
   - Reinitialize the Git repository and add the remote link:
     ```bash
     git init
     git remote add origin <repository-url>
     ```

5. **Add Publish Profile:**
   - Obtain the publish profile from the Azure Function App page.
   - Add this profile to the Github settings of same repository under `Secret` with the parameter name `AZUREAPPSERVICE_PUBLISHPROFILE_FCCB9754D975453B906388F9C6A8FAC7`.

6. **Set Environment Variables:**
   - Ensure the following environment variables are set in your Azure Function App settings with correct Values:
     - `REFRESH_TOKEN`
     - `CLIENT_ZOHO_ID`
     - `CLIENT_ZOHO_SECRET`

7. **Push Changes and Trigger CI/CD Pipeline:**
   - Commit and push your changes to the repository:
     ```bash
     git add .
     git commit -m "Initial commit"
     git push -u origin main
     ```

## Usage

Refer to the [API documentation](https://autonerd.gitbook.io/bubble-service) for details on available endpoints and their usage.



## Contributing

We welcome contributions to this project! If you'd like to contribute, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push the branch (`git push origin feature-branch`).
5. Create a pull request.

