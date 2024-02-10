## Development Guide

Thank you for your interest in contributing to the project! This guide will help you get started with the development process.

The project is designed to be run on linux systems, and the following instructions are tailored to that environment. 
If you are using a different OS, you may need to make some adjustments. 
For Windows, you can use WSL2. It hasn't been tested on macOS, but should work.

### Prerequisites

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/get-docker)
- [Node.js](https://nodejs.org/en/download)
- [Yarn](https://yarnpkg.com/getting-started/install)
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [Make](https://www.gnu.org/software/make)

Additionally on Windows:
- [WSL2](https://docs.microsoft.com/en-us/windows/wsl/install)

### Setup

1. Clone the repository

    ```bash
    git clone git@github.com:sproutmaster/nyuprinters.git
    ```

2. Change into the project directory or open it in your favorite IDE
    
3. Put sample data into the database.
    ```bash
    make seed
    ```

4. There are two ways to run the project, depending on what you'd like to work on. 

    - MINDEV: This works for most cases. Use this to work on the frontend, web and api backend.
   This spins up:
      - statusd: The public serving web server
      - postgres: The database using docker

        ```bash
        make mindev
        ```

    - DEV: This option is when you want to run the full app as if it is in production (not really). Use this if 
   you are on a network with reachable printers. This spins up:
      - statusd: The public serving web server
      - postgres: The database using docker
      - sourced: The backend service for sourcing data from the printers
      - updated: The backend service for updating the printer data

          ```bash
          make dev
          ```
        
### Cleaning up

To stop the running services, you can use the following command:

   ```bash
   make stop
   ```
To delete the database, venv, node modules and start fresh, you can use this make target.
Even though are files are deleted, the data would still persist in a docker volume.

   ```bash
   make clean
   ```

To remove everything and start fresh:

   ```bash
   make reset
   ```
