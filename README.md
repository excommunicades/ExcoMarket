# ExcoMarket Project ✅
![Blog Image](https://raw.githubusercontent.com/excommunicades/ExcoMarket/master/Market.png)

## DESCRIPTION: 

ExcoMarket is a RESTful API built with Flask designed to manage an online marketplace. The project provides full CRUD functionality for products, user management with JWT-based authentication, and supports multi-tenancy to separate user data. It includes features such as product search with natural language queries powered by AI integrations (LangChain, ChromaDB, Ollama), subscription management with real-time Telegram bot notifications. The architecture emphasizes modularity, security, and scalability, enabling seamless integration with web and mobile clients.

## STACK: 

Python3, Flask, MySQL, ChromaDB, LLM/ML API, RabbitMQ, Telegram API, langchain, RAG, AI Agents, multi-tenancy, Event/Listener, Docker, MVC, JWT, Swagger, Pydantic, etc...

## This project demonstrates how to build a custom REST API using Flask. The code serves as a practical guide to the following concepts:

* **Creating a Custom Web Server: Set up a Flask application to handle HTTP requests efficiently.**
* **Building a Full-Featured REST API: Implement CRUD operations for managing products, including creation, reading, updating, and deleting product entries.**
* **User Authentication and Authorization: Use JWT tokens for secure user login and access control.**
* **Data Validation and Serialization: Utilize Pydantic models to validate input data and serialize output responses.**
* **Telegram Bot Implementation: Implement a fully functional Telegram bot with all key features, including user registration, subscription management, and product update alerts.**
* **Search and AI Integration: Leverage LangChain, ChromaDB, and Ollama for natural language product search and AI-powered queries.**
* **Clean and Modular Routing: Organize endpoints with Flask Blueprints for maintainable and scalable API structure.**
* **Error Handling and Response Consistency: Provide clear error messages and proper HTTP status codes for client requests.**

## Key Features 💡

- **User Registration and Authentication:** Implements secure user management with JWT-based authentication and token handling.
  secure token handling.
- **Product Management:** Provides full CRUD functionality for products via a RESTful API, allowing creation, retrieval, update, and deletion of product entries.
- **Data Validation and Serialization:** Uses Pydantic models to validate input data and serialize API responses consistently.
- **Fully Functional Telegram Bot:** Offers real-time user interaction including registration, subscription management, and product update notifications.
- **AI-Powered Search:** Incorporates LangChain, ChromaDB, and Ollama to enable natural language search and intelligent product queries.
- **Modular API Structure:** Organizes endpoints using Flask Blueprints for scalable and maintainable code architecture.

# Installation Guide 📕:

### Prerequisites 💻

Ensure you have Docker and Docker Compose installed on your machine. You can download them from:

- Docker: [Get Docker](https://docs.docker.com/get-docker/) 🐳
- Docker Compose: [Docker Compose](https://docs.docker.com/compose/install/) 🐳

### Environment Variables
Create a `.env` file in the root of your project directory with the following content:
```
# MYSQL DB

MYSQL_USER=your_db_user
MYSQL_HOST_PORT=mysql:3306
MYSQL_DATABASE=your_db_name
MYSQL_PASSWORD=your_db_user_password
MYSQL_ROOT_PASSWORD=your_db_root_password

# FLASK
BACKEND_HOST=web
SECRET_KEY=your_secret_key

# REDIS, RABBITMQ HOSTS

REDIS_HOST=redis
RABBIT_MQ_HOST=rabbitmq

# TG

TG_BOT_TOKEN=your_tg_bot_token

# AI, CHROMADB HOST, OLLAMA API

CHROMADB_HOST=chroma
OLLAMA_API=http://ollama:11434/api/chat
LLM_MODEL_NAME=mistral:7b-instruct # You can set your own
```

# Start the Services 🚪

1. **Clone the repository:** ```git clone https://github.com/excommunicades/ExcoMarket.git``` -> ```cd ExcoMarket```
2. **Create `.env` file**
3. **Build and run the application with Docker Compose:** ```docker-compose up --build```
4. **Pull LLM Model to ollama while ollama docker container is running:** ```docker exec ollama ollama pull mistral:7b-instruct```

# Stopping the Services 🚪

**To stop all running services, you can use:** ```docker-compose down```

### API Endpoints

#### Auth
- **POST** /auth/login: Login a user  
- **POST** /auth/register: Register a new user  
- **POST** /auth/token/refresh: Refresh JWT access token  

#### Manage
- **GET** /manage/health: Check database connection status  
- **POST** /manage/populate/products: Populate database with sample products  
- **GET** /manage/users: Get all users  

#### Products
- **GET** /products: Get all available (unsold) products  
- **POST** /products: Create a new product  
- **POST** /products/purchase/{product_id}: Purchase a product by ID  
- **DELETE** /products/{product_id}: Delete product by ID  
- **GET** /products/{product_id}: Get product details by ID  
- **PATCH** /products/{product_id}: Update product by ID  

#### Profile
- **GET** /profile/: Get user profile with their active products  

#### Subscription
- **POST** /subscriptions/subscribe/{seller_id}: Subscribe to a seller  
- **POST** /subscriptions/unsubscribe/{seller_id}: Unsubscribe from a seller  

#### Wallet
- **POST** /wallet/clear: Reset the authenticated user's wallet balance to zero  
- **POST** /wallet/reward: Reward the authenticated user  

# IMPORTANT ♻️

Currently, products from the database are indexed for the chromedb collection at docker startup as index_chromadb service. If you have created a new product, use the following command:
**Execute the command while docker services are running:** ```docker-compose run index_chromadb```

Timely indexing is necessary for the correct operation of the AI assistant for searching products.

# Conclusion

This project was created to demonstrate my desire to adapt and learn new tools, as well as to improve and deepen my expertise in the technologies I already know.

## Authors 😎

- **Stepanenko Daniil** - "ExcoMarket"