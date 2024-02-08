## Powerline E2E Messaging Service
Intro: Work in progress development space for a personal messaging service using self hosted nodes or via Azure App Service deployments.

Currently using an MSSQL DB for testing but this will get converted over to SQLite3 to run in a container at some point. Just getting the functional side working then adding some encryption to play around with the most effective techniques

Includes Firebase integration for push notifications and statistics

## Targeted for: IOS/Android/UWP + Web Clients

Section to be updated post deployment and architecture diagrams

### To Run API:
Ensure all requirements as specified in requirements.txt are installed
Run: uvicorn api:app --reload to start server process

### To Run Client
Ensure requirements are met:
    - cd Powerline\powerline_client
    - yarn start

### React Front End
Standalone React front end moved to its own branch at:
- https://github.com/Darcy-NR/Web-App-Powerline
