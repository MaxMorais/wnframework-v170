# wnframework v170 Dockerized

## Overview

wnframework v170, the predecessor of the renowned frappe framework and ERPNext, is now available in a Docker container! This project is aimed at enthusiasts and developers who appreciate nostalgia and the evolution of technology. Dive into the classic era of wnframework with the ease and flexibility of a modern Docker environment.

## Getting Started

### Prerequisites

- Docker
- Basic knowledge of Docker and wnframework

### Installation

1. **Clone the Repository:**


    git clone https://github.com/MaxMorais/wnframework-v170


2. **Build the Docker Image:**

    
    docker build -t wnframework-v170 .


3. **Run the Container:**


    docker run -d -p 8000:8000 wnframework-v170


### Accessing the Application

After starting the container, wnframework v170 will be accessible at `http://localhost:8000`.

## Features

- Complete wnframework v170 environment
- Setup with SQLite instead of MySQL due SQLInjections security flaws
- Preconfigured Docker setup for easy deployment
- Ideal for development, testing, and nostalgic exploration

## Contributing

Contributions are welcome! If you have improvements or fixes, please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -am 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT - see the LICENSE.md file for details.

## Acknowledgments

- Original creators and community of wnframework
    - Frappe Team

- Contributors to this Dockerized version
    - Maxwell Morais

## Contact

For any inquiries or contributions, please contact Maxwell Morais at max.morais.dmm@gmail.com .

---

Enjoy the journey back in time with wnframework v170 in Docker!

